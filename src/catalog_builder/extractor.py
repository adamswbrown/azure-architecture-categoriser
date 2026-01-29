"""Metadata extraction from architecture documents."""

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import quote

from .config import get_config
from .parser import MarkdownParser, ParsedDocument
from .schema import ArchitectureEntry, ClassificationMeta, ExtractionConfidence

# Services that are typically supporting (observability, security, operations)
SUPPORTING_SERVICE_PATTERNS = [
    'monitor', 'log analytics', 'application insights', 'sentinel',
    'key vault', 'defender', 'security center',
    'policy', 'advisor', 'cost management', 'automation',
    'backup', 'site recovery', 'bastion',
    'dns', 'traffic manager', 'ddos',
]

# Core service categories that realize the pattern
CORE_SERVICE_CATEGORIES = [
    # Compute
    'app service', 'functions', 'kubernetes', 'container', 'virtual machine',
    'batch', 'service fabric', 'spring', 'web app',
    # Data
    'sql', 'cosmos', 'storage', 'redis', 'postgresql', 'mysql', 'synapse',
    'data factory', 'databricks', 'data lake', 'event hub', 'stream analytics',
    # Integration
    'api management', 'logic app', 'service bus', 'event grid',
    # Networking (core)
    'application gateway', 'front door', 'load balancer', 'firewall',
    'virtual network', 'expressroute', 'vpn', 'private link',
    # AI
    'openai', 'cognitive', 'machine learning', 'search',
]


class MetadataExtractor:
    """Extracts metadata from architecture documents."""

    def __init__(self, parser: MarkdownParser):
        self.parser = parser

    def extract(
        self,
        doc: ParsedDocument,
        repo_root: Path,
        last_modified: Optional[datetime] = None
    ) -> ArchitectureEntry:
        """Extract metadata and create an architecture entry."""
        rel_path = str(doc.path.relative_to(repo_root)).replace('\\', '/')

        # Generate architecture ID from path
        arch_id = self._generate_id(rel_path)

        # Extract title and description
        title = self._extract_title(doc)
        description = self._extract_description(doc)

        # Build Learn URL
        learn_url = self._build_learn_url(rel_path)

        # Extract and classify Azure services
        all_services = self.parser.extract_azure_services(doc)
        core_services, supporting_services = self._classify_services(all_services)

        # Infer pattern name from title and services
        pattern_name = self._infer_pattern_name(title, core_services, doc)

        # Extract diagram assets
        diagrams = self._extract_diagrams(doc, rel_path)

        # Create entry with extracted values
        entry = ArchitectureEntry(
            architecture_id=arch_id,
            name=title,
            pattern_name=pattern_name,
            pattern_name_confidence=ClassificationMeta(
                confidence=ExtractionConfidence.AI_SUGGESTED,
                source="title_and_services"
            ),
            description=description,
            source_repo_path=rel_path,
            learn_url=learn_url,
            core_services=core_services,
            supporting_services=supporting_services,
            services_confidence=ClassificationMeta(
                confidence=ExtractionConfidence.AI_SUGGESTED,
                source="content_analysis"
            ),
            diagram_assets=diagrams,
            last_repo_update=last_modified,
        )

        # Add extraction warnings
        if not title:
            entry.extraction_warnings.append("Could not extract title")
        if not description:
            entry.extraction_warnings.append("Could not extract description")
        if not core_services:
            entry.extraction_warnings.append("No core Azure services detected")
        if not diagrams:
            entry.extraction_warnings.append("No architecture diagrams found")

        return entry

    def _classify_services(self, services: list[str]) -> tuple[list[str], list[str]]:
        """Classify services into core and supporting categories."""
        core = []
        supporting = []

        for service in services:
            service_lower = service.lower()

            # Check if it's a supporting service
            is_supporting = any(
                pattern in service_lower
                for pattern in SUPPORTING_SERVICE_PATTERNS
            )

            if is_supporting:
                supporting.append(service)
            else:
                # Check if it matches core service patterns
                is_core = any(
                    pattern in service_lower
                    for pattern in CORE_SERVICE_CATEGORIES
                )
                if is_core:
                    core.append(service)
                else:
                    # Default to supporting if unrecognized
                    supporting.append(service)

        return core, supporting

    def _infer_pattern_name(
        self,
        title: str,
        core_services: list[str],
        doc: ParsedDocument
    ) -> str:
        """Infer a normalized pattern name representing architectural intent.

        Pattern names should describe WHAT the architecture does, not just
        the article title. For example:
        - "Zone-Redundant App Service with Private Link"
        - "Multi-Region AKS with Traffic Manager"
        - "Event-Driven Microservices on Container Apps"
        """
        # Start with the title but clean it up
        pattern = title

        # Remove common article prefixes/suffixes
        prefixes_to_remove = [
            'architecture for ', 'reference architecture for ',
            'example: ', 'tutorial: ', 'how to ',
            'azure ', 'microsoft ',
        ]
        suffixes_to_remove = [
            ' - azure architecture center', ' on azure',
            ' architecture', ' pattern',
        ]

        pattern_lower = pattern.lower()
        for prefix in prefixes_to_remove:
            if pattern_lower.startswith(prefix):
                pattern = pattern[len(prefix):]
                pattern_lower = pattern.lower()

        for suffix in suffixes_to_remove:
            if pattern_lower.endswith(suffix):
                pattern = pattern[:-len(suffix)]
                pattern_lower = pattern.lower()

        # If the pattern is too generic, try to enrich it with core services
        generic_titles = ['architecture', 'overview', 'introduction', 'guide']
        if pattern_lower in generic_titles or len(pattern) < 10:
            if core_services:
                # Build pattern from primary services
                primary = core_services[:3]  # Top 3 services
                pattern = ' with '.join(primary)

        # Try to extract availability/topology hints from content
        content_lower = doc.content.lower()
        topology_hints = []

        if 'multi-region' in content_lower or 'multiple regions' in content_lower:
            topology_hints.append('Multi-Region')
        elif 'zone-redundant' in content_lower or 'availability zone' in content_lower:
            topology_hints.append('Zone-Redundant')

        if 'active-active' in content_lower:
            topology_hints.append('Active-Active')
        elif 'active-passive' in content_lower:
            topology_hints.append('Active-Passive')

        if 'private endpoint' in content_lower or 'private link' in content_lower:
            topology_hints.append('with Private Networking')

        if 'mission-critical' in content_lower or 'mission critical' in content_lower:
            topology_hints.insert(0, 'Mission-Critical')

        # Prepend topology hints if not already in pattern
        for hint in topology_hints:
            if hint.lower() not in pattern.lower():
                pattern = f"{hint} {pattern}"

        # Clean up and title case
        pattern = pattern.strip()
        if pattern:
            # Title case but preserve acronyms
            words = pattern.split()
            result = []
            for word in words:
                if word.isupper() and len(word) > 1:
                    result.append(word)  # Keep acronyms
                else:
                    result.append(word.capitalize())
            pattern = ' '.join(result)

        return pattern or title

    def _generate_id(self, rel_path: str) -> str:
        """Generate a unique ID from the file path."""
        # Remove docs/ prefix and .md extension
        path = rel_path
        if path.startswith('docs/'):
            path = path[5:]
        if path.endswith('.md'):
            path = path[:-3]

        # Replace special chars with dashes
        path = re.sub(r'[^a-zA-Z0-9]+', '-', path)
        path = path.strip('-').lower()

        # Ensure uniqueness with hash suffix if path is too long
        if len(path) > 60:
            hash_suffix = hashlib.md5(rel_path.encode()).hexdigest()[:8]
            path = path[:50] + '-' + hash_suffix

        return path

    def _extract_title(self, doc: ParsedDocument) -> str:
        """Extract the title from the document."""
        # Priority: frontmatter title > first H1 > filename
        if doc.title:
            return doc.title

        # Try first H1
        for level, heading in doc.headings:
            if level == 1:
                return heading

        # Fall back to filename
        return doc.path.stem.replace('-', ' ').replace('_', ' ').title()

    def _extract_description(self, doc: ParsedDocument) -> str:
        """Extract description from the document."""
        # Priority: frontmatter description > first paragraph
        if doc.description:
            return doc.description

        # Try to get first substantial paragraph
        content = doc.content.strip()
        paragraphs = re.split(r'\n\s*\n', content)

        for para in paragraphs:
            # Skip headings, images, includes
            para = para.strip()
            if para.startswith('#'):
                continue
            if para.startswith('!'):
                continue
            if para.startswith('[!INCLUDE'):
                continue
            if len(para) > 50:
                # Clean up markdown
                clean = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', para)
                clean = re.sub(r'[*_`]', '', clean)
                return clean[:500]

        return ""

    def _build_learn_url(self, rel_path: str) -> Optional[str]:
        """Build the Microsoft Learn URL for the document."""
        config = get_config().urls

        # Remove docs/ prefix and .md extension
        path = rel_path
        if path.startswith('docs/'):
            path = path[5:]
        if path.endswith('.md'):
            path = path[:-3]
        if path.endswith('/index'):
            path = path[:-6]

        # URL encode the path
        path = quote(path, safe='/')

        return f"{config.learn_base_url}/{path}"

    def _extract_diagrams(self, doc: ParsedDocument, rel_path: str) -> list[str]:
        """Extract diagram asset paths."""
        diagrams = []
        doc_dir = Path(rel_path).parent

        for image in doc.images:
            # Normalize path
            if image.startswith('./'):
                image = image[2:]
            if image.startswith('../'):
                # Resolve relative path
                image_path = (doc_dir / image).as_posix()
            elif not image.startswith('http'):
                image_path = (doc_dir / image).as_posix()
            else:
                # Skip external URLs
                continue

            # Check if it looks like a diagram
            lower = image.lower()
            if any(x in lower for x in ['architecture', 'diagram', 'flow', '.svg']):
                diagrams.append(image_path)
            elif lower.endswith(('.svg', '.png')):
                diagrams.append(image_path)

        return diagrams


class GitMetadataExtractor:
    """Extracts metadata from git repository."""

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self._repo = None

    def _get_repo(self):
        """Lazy load git repo."""
        if self._repo is None:
            try:
                import git
                self._repo = git.Repo(self.repo_root)
            except Exception:
                self._repo = False
        return self._repo if self._repo else None

    def get_last_modified(self, file_path: Path) -> Optional[datetime]:
        """Get the last modified date for a file from git."""
        repo = self._get_repo()
        if not repo:
            return None

        try:
            rel_path = str(file_path.relative_to(self.repo_root))
            commits = list(repo.iter_commits(paths=rel_path, max_count=1))
            if commits:
                return datetime.fromtimestamp(commits[0].committed_date)
        except Exception:
            pass

        return None

    def get_current_commit(self) -> Optional[str]:
        """Get the current commit hash."""
        repo = self._get_repo()
        if not repo:
            return None

        try:
            return repo.head.commit.hexsha
        except Exception:
            return None
