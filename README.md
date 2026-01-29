# Azure Architecture Catalog Builder

A CLI tool that compiles Azure Architecture Center documentation into a structured architecture catalog.

## Purpose

This tool runs at **build time only**. It does NOT perform scoring, read application data, or produce recommendations. Its only responsibility is to create a static catalog describing architecture patterns and their architectural intent.

The output (`architecture-catalog.json`) is designed to be consumed by browser-based applications for runtime architecture matching.

## Installation

```bash
# Clone this repository
git clone https://github.com/adamswbrown/azure-architecture-categoriser-.git
cd azure-architecture-categoriser-

# Install the package
pip install -e .
```

## Usage

### Build the Catalog

```bash
# Clone the Azure Architecture Center repository
git clone https://github.com/MicrosoftDocs/architecture-center.git

# Build the catalog
catalog-builder build-catalog \
  --repo-path ./architecture-center \
  --out architecture-catalog.json
```

### Filter by Category or Product

```bash
# Filter by Azure category
catalog-builder build-catalog --repo-path ./repo --category containers

# Filter by Azure product (supports prefix matching)
catalog-builder build-catalog --repo-path ./repo --product azure-kubernetes

# Require YamlMime:Architecture files only
catalog-builder build-catalog --repo-path ./repo --require-yml
```

### List Available Filters

```bash
# Show all available filter values
catalog-builder list-filters --repo-path ./architecture-center

# Show only products with 5+ documents
catalog-builder list-filters --repo-path ./repo --type products --min-count 5
```

### Inspect the Catalog

```bash
# List all architectures
catalog-builder inspect --catalog architecture-catalog.json

# Filter by family
catalog-builder inspect --catalog architecture-catalog.json --family cloud_native

# View specific architecture details
catalog-builder inspect --catalog architecture-catalog.json --id example-scenario-web-app-baseline
```

### View Statistics

```bash
catalog-builder stats --catalog architecture-catalog.json
```

## Catalog Schema

Each architecture entry includes:

### Identity
- `architecture_id`: Unique identifier derived from path
- `name`: Human-readable architecture name (workload-intent focused)
- `pattern_name`: Normalized pattern name describing architectural intent
- `description`: Brief description
- `source_repo_path`: Path in source repository
- `learn_url`: Microsoft Learn URL

### Browse Metadata (from YamlMime:Architecture)
- `browse_tags`: Tags for filtering (e.g., `["Azure", "Containers", "Web"]`)
- `browse_categories`: Categories for classification (e.g., `["Architecture", "Reference", "Containers"]`)
- `catalog_quality`: Quality level - `curated` (from YML), `ai_enriched`, or `ai_suggested`

### Classification
- `family`: foundation, iaas, paas, cloud_native, data, integration, specialized
- `workload_domain`: web, data, integration, security, ai, infrastructure, general

### Architectural Expectations
- `expected_runtime_models`: monolith, n_tier, api, microservices, event_driven, batch, mixed
- `expected_characteristics`:
  - `containers`: true/false/optional
  - `stateless`: true/false/optional
  - `devops_required`: boolean (true for AKS, Container Apps, Functions, App Service)
  - `ci_cd_required`: boolean (true for PaaS and container workloads)
  - `private_networking_required`: boolean (detected from content)

### Supported Change Models
- `supported_treatments`: retire, tolerate, rehost, replatform, refactor, replace, rebuild, retain
- `supported_time_categories`: tolerate, migrate, invest, eliminate

### Operational Expectations
- `availability_models`: single_region, zone_redundant, multi_region_active_passive, multi_region_active_active
- `security_level`: basic, enterprise, regulated, highly_regulated
- `operating_model_required`: traditional_it, transitional, devops, sre

### Cost & Complexity
- `cost_profile`: cost_minimized, balanced, scale_optimized, innovation_first
- `complexity`: implementation (low/medium/high), operations (low/medium/high)

### Exclusion Rules
- `not_suitable_for`: Scenarios where this architecture is not suitable
  - `low_devops_maturity`, `single_vm_workloads`, `no_container_experience`, `stateful_apps`
  - `greenfield_only`, `simple_workloads`, `windows_only`, `linux_only`
  - `low_maturity_teams`, `regulated_workloads`, `low_budget`, `skill_constrained`

### Metadata
- `core_services`: Azure services required to realize the pattern (compute, data, networking)
- `supporting_services`: Supporting services for observability, security, and operations
- `diagram_assets`: Paths to architecture diagrams
- `last_repo_update`: Last modification date from git

## Automation Levels

### Curated (from YamlMime:Architecture)
- Browse tags and categories
- Product associations
- Document classification (reference-architecture, example-scenario, solution-idea)

### AI-Suggested (Human Review Recommended)
- Pattern name inference
- Runtime model classification
- Treatment and TIME category suggestions
- Security level detection
- Operating model requirements
- Complexity ratings

### Detected from Content
- `devops_required`: True when containers, AKS, or DevOps keywords present
- `ci_cd_required`: True for serverless/PaaS services
- `private_networking_required`: True when private endpoint/link mentioned

## Detection Heuristics

Architecture candidates are identified by:

1. **YamlMime:Architecture**: Files with paired `.yml` metadata (highest confidence)
2. **Location**: Files in `docs/example-scenario/`, workload domain folders
3. **Diagrams**: Contains SVG or PNG architecture diagrams
4. **Sections**: Contains Architecture, Components, or Diagram sections
5. **Keywords**: References "reference architecture", "baseline architecture", "solution idea"

### Excluded Content
- Non-architecture layouts (hub pages, landing pages, tutorials)
- `docs/guide/` - Conceptual guidance
- Pattern descriptions
- Icons, templates, includes
- Very short content with no diagrams
- High link density pages (navigation pages)

## Configuration

Generate a default config file:

```bash
catalog-builder init-config --out catalog-config.yaml
```

See [CONFIGURATION.md](CONFIGURATION.md) for full configuration reference.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with verbose output
catalog-builder build-catalog --repo-path ./architecture-center --out catalog.json -v
```

## Sample Output

```json
{
  "architecture_id": "example-scenario-aks-baseline",
  "name": "Enterprise-grade AKS Cluster With Private Networking And Ingress",
  "pattern_name": "Enterprise-grade AKS Cluster With Private Networking And Ingress",
  "pattern_name_confidence": {
    "confidence": "curated",
    "source": "yml_metadata"
  },
  "browse_tags": ["Azure", "Containers"],
  "browse_categories": ["Architecture", "Reference", "Containers"],
  "catalog_quality": "curated",
  "expected_characteristics": {
    "containers": "true",
    "stateless": "optional",
    "devops_required": true,
    "ci_cd_required": true,
    "private_networking_required": true
  },
  "family": "cloud_native",
  "workload_domain": "infrastructure",
  "expected_runtime_models": ["microservices"],
  "supported_treatments": ["refactor", "rebuild"],
  "operating_model_required": "devops",
  "security_level": "enterprise"
}
```

## Core Principles

1. **This tool produces knowledge, not decisions**
2. **Output is deterministic and versionable**
3. **Catalog is consumable entirely client-side**
4. **Architecture intent must be explicit and explainable**
5. **Human-readable names first, machine-friendly second**
6. **Curated metadata from authoritative sources when available**
7. **Clean over complete** - Better to lose services than include dirty/prose data

## Prompt Documentation

The design decisions and rules are documented in the `prompts/` folder:

- [catalog-builder-prompt-v1.md](prompts/catalog-builder-prompt-v1.md) - Catalog builder specification
- [architecture-scorer-prompt-v1.md](prompts/architecture-scorer-prompt-v1.md) - Architecture scorer specification

**Catalog Builder prompt** covers:
- Service extraction rules (allow-list matching, prose filtering)
- Pattern name inference and truncation rules
- Quality level determination criteria
- Classification keyword scoring
- Junk name detection

**Architecture Scorer prompt** covers:
- Input normalization and signal extraction
- Dynamic clarification question generation
- Eligibility filtering rules
- Scoring weights and confidence penalties
- Interactive CLI mode

## Architecture

This tool is part of a three-tier architecture:

| Component | Role | Characteristics |
|-----------|------|-----------------|
| **Catalog Builder** | Neutral catalog compiler | Build-time, deterministic, no scoring |
| **Architecture Scorer** | Scoring and recommendation | Runtime, explainable, interactive |
| **Browser App** (future) | User interface | Explainability and confirmation |

---

## Architecture Scorer

The Architecture Scorer is the second component - a runtime engine that evaluates application contexts against the catalog and returns ranked recommendations with explanations.

### Installation

The scorer is included when you install the package:

```bash
pip install -e .
```

### Usage

```bash
# Score an application context against the catalog
architecture-scorer score \
  --catalog architecture-catalog.json \
  --context app-context.json

# Interactive mode (default) - prompts for answers to clarification questions
architecture-scorer score -c catalog.json -x context.json

# Non-interactive mode - skip question prompts
architecture-scorer score -c catalog.json -x context.json --no-interactive

# Provide answers directly
architecture-scorer score -c catalog.json -x context.json \
  -a treatment=replatform \
  -a security_level=enterprise \
  -a operating_model=devops

# Show only clarification questions
architecture-scorer questions -c catalog.json -x context.json

# Validate inputs
architecture-scorer validate -c catalog.json -x context.json
```

### Interactive Question Mode

By default, the scorer runs in interactive mode. When clarification questions are generated, you're prompted to answer them:

```
╭─────────────────────────────────────────────────────────────────────────────╮
│  Clarification Questions                                                    │
╰─────────────────────────────────────────────────────────────────────────────╯

Question 1 of 3:
What security/compliance level is required for this application?
Current inference: basic (confidence: LOW)

    1. Basic - Standard security practices, no specific compliance
    2. Enterprise - Enterprise security (Zero Trust, private endpoints)
  → 3. Regulated - Industry compliance (SOC 2, ISO 27001, GDPR)
    4. Highly Regulated - Strict compliance (HIPAA, PCI-DSS, FedRAMP)

Enter choice (1-4) or value [press Enter to keep current]:
```

Enter a number (1-4) to select an option, type a value directly, or press Enter to keep the current inference.

### Clarification Questions

Questions are **dynamically generated** based on signal confidence levels. The scorer only asks when:
- A signal has LOW or UNKNOWN confidence
- The answer materially affects eligibility or scoring

| Question | Dimension | When Asked |
|----------|-----------|------------|
| Migration strategy | `treatment` | No declared treatment, low confidence |
| Strategic investment posture | `time_category` | UNKNOWN confidence only |
| Availability requirements | `availability` | Low confidence |
| Security/compliance level | `security_level` | No compliance requirements specified |
| Operational maturity | `operating_model` | Low confidence |
| Cost optimization priority | `cost_posture` | Low confidence |

### Confidence Levels

Each recommendation includes a confidence assessment based on **four factors**:

| Level | Requirements | Description |
|-------|--------------|-------------|
| **High** | Score ≥75% AND Penalty <10% AND Low Signals ≤1 AND Assumptions ≤2 | Strong match, minimal uncertainty |
| **Medium** | Score ≥50% AND Penalty <20% AND Low Signals ≤3 | Reasonable match with some uncertainty |
| **Low** | Does not meet Medium criteria | Weak match or many assumptions |

**Confidence Penalties by Signal:**
- HIGH confidence: 0% penalty
- MEDIUM confidence: 5% penalty per signal
- LOW confidence: 15% penalty per signal
- UNKNOWN confidence: 25% penalty per signal

### Why Confidence Can Remain "Low" Even After Answering All Questions

The confidence calculation checks **9 intent signals**, but only **6 are addressable via clarification questions**:

| Signal | Question Available? | Source When No Question |
|--------|---------------------|------------------------|
| `treatment` | ✅ Yes | User answer or App Mod |
| `time_category` | ✅ Yes | User answer or treatment inference |
| `availability_requirement` | ✅ Yes | User answer or business criticality |
| `security_requirement` | ✅ Yes | User answer or compliance detection |
| `operational_maturity_estimate` | ✅ Yes | User answer or technology detection |
| `cost_posture` | ✅ Yes | User answer or heuristics |
| `likely_runtime_model` | ❌ No | Derived from App Mod or technology |
| `modernization_depth_feasible` | ❌ No | Derived from App Mod results |
| `cloud_native_feasibility` | ❌ No | Derived from App Mod results |

**Example: Why a scenario might show "Low" confidence with all questions answered:**

```
Application: GlobalTradingPlatform
Answers Provided: 6 (all questions answered)

Signals at HIGH confidence (from answers):
  • treatment: replatform ✅
  • time_category: migrate ✅
  • availability: zone_redundant ✅
  • security_level: enterprise ✅
  • operating_model: transitional ✅
  • cost_posture: balanced ✅

Signals at LOW/UNKNOWN confidence (no App Mod data):
  • likely_runtime_model: event_driven (LOW) ❌
  • modernization_depth_feasible: unknown (UNKNOWN) ❌
  • cloud_native_feasibility: unknown (UNKNOWN) ❌

Low confidence count: 3 (exactly at threshold)
Top recommendation score: 50% (at threshold)
Catalog quality: example_only (70% weight applied)

Result: "Low" confidence
  - 3 low-confidence signals is borderline
  - 50% score barely meets threshold
  - example_only quality reduces effective scores
```

**To achieve "Medium" or "High" confidence:**
1. **Provide App Mod results** - These derive the 3 non-questionable signals (runtime model, modernization depth, cloud-native feasibility) at HIGH confidence
2. **Better catalog coverage** - Higher-quality (`curated`) architectures with better score matches
3. **Higher base scores** - Better alignment between application characteristics and available architectures

### Output Example

```
╭─────────────────────────────────────────────────────────────────────────────╮
│  Architecture Scoring Results                                               │
╰─────────────────────────────────────────────────────────────────────────────╯

Application: PaymentGateway
Treatment: refactor | TIME Category: invest
Eligible Architectures: 12 | Excluded: 159

Your Answers Applied:
  • security_level: regulated
  • operating_model: devops

╭─────────────────────────────────────────────────────────────────────────────╮
│  Top 5 Recommendations                                                      │
╰─────────────────────────────────────────────────────────────────────────────╯

1. AKS Baseline Cluster Architecture
   Score: 74% | Confidence: MEDIUM | Quality: curated
   URL: https://learn.microsoft.com/en-us/azure/architecture/...

   ✓ Matched: treatment_alignment, platform_compatibility, service_overlap
   ✗ Gaps: availability_alignment (partial)
   ⚠ Assumptions: runtime_model inferred from app type
```

### Scoring Weights

| Dimension | Weight | Description |
|-----------|--------|-------------|
| treatment_alignment | 20% | Gartner 8R treatment match |
| platform_compatibility | 15% | App Mod platform status |
| app_mod_recommended | 10% | Boost for App Mod recommended targets |
| runtime_model_compatibility | 10% | Runtime model match |
| service_overlap | 10% | Approved Azure services match |
| availability_alignment | 10% | Availability model match |
| operating_model_fit | 8% | Operational maturity fit |
| complexity_tolerance | 7% | Complexity vs business criticality |
| browse_tag_overlap | 5% | Relevant browse tags match |
| cost_posture_alignment | 5% | Cost profile match |

### Catalog Quality Weights

| Quality | Weight | Description |
|---------|--------|-------------|
| curated | 100% | From authoritative YamlMime:Architecture |
| ai_enriched | 95% | Partial authoritative data |
| ai_suggested | 85% | AI-extracted metadata |
| example_only | 70% | Example scenarios, not prescriptive |

## Version

**v1.1** - Architecture Scorer release:
- Interactive CLI with numbered question options
- Dynamic clarification question generation
- Confidence level calculations with penalty system
- Cost posture question dimension added
- User answers displayed in scoring summary

**v1.0** - Initial release with:
- 171 architectures from Azure Architecture Center
- Clean Azure services extraction (allow-list validated)
- Junk pattern name detection
- Enhanced classifications (Gartner 8R, TIME model)
- Quality differentiation (curated vs example_only)

## License

MIT
