# Catalog Builder

The Catalog Builder compiles Azure Architecture Center documentation into a structured architecture catalog that can be used for matching applications to recommended architectures.

## Overview

This is a **build-time tool** that:
- Parses the Azure Architecture Center repository
- Extracts architecture patterns, services, and metadata
- Produces a deterministic, versionable `architecture-catalog.json`

The catalog is consumed by the [Architecture Recommendations App](./recommendations-app.md) for runtime scoring.

## Installation

```bash
# Clone the repository
git clone https://github.com/adamswbrown/azure-architecture-categoriser-.git
cd azure-architecture-categoriser-

# Install the package
pip install -e .
```

## Quick Start

```bash
# 1. Clone the Azure Architecture Center repository
git clone https://github.com/MicrosoftDocs/architecture-center.git

# 2. Build the catalog
catalog-builder build-catalog \
  --repo-path ./architecture-center \
  --out architecture-catalog.json

# 3. Inspect the results
catalog-builder stats --catalog architecture-catalog.json
```

## CLI Commands

### build-catalog

Build the architecture catalog from source documentation.

```bash
catalog-builder build-catalog \
  --repo-path ./architecture-center \
  --out architecture-catalog.json
```

**Options:**
| Option | Description |
|--------|-------------|
| `--repo-path` | Path to cloned architecture-center repository |
| `--out` | Output file path (default: `architecture-catalog.json`) |
| `--category` | Filter by Azure category (e.g., `containers`) |
| `--product` | Filter by Azure product (supports prefix matching) |
| `--require-yml` | Only include files with YamlMime:Architecture metadata |
| `-v, --verbose` | Enable verbose output |

### list-filters

Show available filter values from the repository.

```bash
catalog-builder list-filters --repo-path ./architecture-center
```

**Options:**
| Option | Description |
|--------|-------------|
| `--type` | Filter type: `categories`, `products`, or `all` |
| `--min-count` | Only show values with N+ documents |

### inspect

Inspect catalog contents.

```bash
# List all architectures
catalog-builder inspect --catalog architecture-catalog.json

# Filter by family
catalog-builder inspect --catalog architecture-catalog.json --family cloud_native

# View specific architecture
catalog-builder inspect --catalog architecture-catalog.json --id example-scenario-aks-baseline
```

### stats

Display catalog statistics.

```bash
catalog-builder stats --catalog architecture-catalog.json
```

### init-config

Generate a default configuration file.

```bash
catalog-builder init-config --out catalog-config.yaml
```

## GUI Mode

A graphical interface is also available for building and inspecting catalogs:

```bash
# Install GUI dependencies
pip install -e ".[gui]"

# Launch the GUI
catalog-builder-gui
```

The GUI provides:
- Visual catalog building with progress tracking
- Architecture browsing and inspection
- Quality statistics and charts
- Export functionality

## Catalog Schema

Each architecture entry includes:

### Identity
| Field | Description |
|-------|-------------|
| `architecture_id` | Unique identifier derived from path |
| `name` | Human-readable architecture name |
| `pattern_name` | Normalized pattern name |
| `description` | Brief description |
| `source_repo_path` | Path in source repository |
| `learn_url` | Microsoft Learn URL |

### Classification
| Field | Description |
|-------|-------------|
| `family` | foundation, iaas, paas, cloud_native, data, integration, specialized |
| `workload_domain` | web, data, integration, security, ai, infrastructure, general |
| `catalog_quality` | curated, ai_enriched, ai_suggested, example_only |

### Architectural Expectations
| Field | Description |
|-------|-------------|
| `expected_runtime_models` | monolith, n_tier, api, microservices, event_driven, batch, mixed |
| `expected_characteristics` | containers, stateless, devops_required, ci_cd_required, private_networking_required |

### Supported Change Models
| Field | Description |
|-------|-------------|
| `supported_treatments` | Gartner 8R: retire, tolerate, rehost, replatform, refactor, replace, rebuild, retain |
| `supported_time_categories` | TIME model: tolerate, migrate, invest, eliminate |

### Operational Expectations
| Field | Description |
|-------|-------------|
| `availability_models` | single_region, zone_redundant, multi_region_active_passive, multi_region_active_active |
| `security_level` | basic, enterprise, regulated, highly_regulated |
| `operating_model_required` | traditional_it, transitional, devops, sre |

### Azure Services
| Field | Description |
|-------|-------------|
| `core_services` | Required Azure services (compute, data, networking) |
| `supporting_services` | Supporting services (monitoring, security, operations) |

### Assets
| Field | Description |
|-------|-------------|
| `diagram_assets` | Paths to architecture diagram images |
| `browse_tags` | Tags for filtering |
| `browse_categories` | Categories for classification |

## Quality Levels

| Level | Source | Description |
|-------|--------|-------------|
| **curated** | YamlMime:Architecture | Authoritative metadata from Microsoft |
| **ai_enriched** | Partial authoritative | Some metadata curated, rest inferred |
| **ai_suggested** | Content analysis | All metadata extracted by AI |
| **example_only** | Example scenarios | Not prescriptive reference architectures |

## Detection Heuristics

Architecture candidates are identified by:

1. **YamlMime:Architecture** - Files with paired `.yml` metadata (highest confidence)
2. **Location** - Files in `docs/example-scenario/`, workload domain folders
3. **Diagrams** - Contains SVG or PNG architecture diagrams
4. **Sections** - Contains Architecture, Components, or Diagram sections
5. **Keywords** - References "reference architecture", "baseline architecture", "solution idea"

### Excluded Content
- Non-architecture layouts (hub pages, landing pages, tutorials)
- `docs/guide/` - Conceptual guidance
- Pattern descriptions without implementations
- Icons, templates, includes
- Very short content with no diagrams
- High link density pages (navigation pages)

## Configuration

See [CONFIGURATION.md](../CONFIGURATION.md) for the full configuration reference.

## Example Output

```json
{
  "architecture_id": "example-scenario-aks-baseline",
  "name": "Enterprise-grade AKS Cluster With Private Networking And Ingress",
  "pattern_name": "Enterprise-grade AKS Cluster With Private Networking And Ingress",
  "catalog_quality": "curated",
  "family": "cloud_native",
  "workload_domain": "infrastructure",
  "expected_runtime_models": ["microservices"],
  "expected_characteristics": {
    "containers": "true",
    "stateless": "optional",
    "devops_required": true,
    "ci_cd_required": true,
    "private_networking_required": true
  },
  "supported_treatments": ["refactor", "rebuild"],
  "operating_model_required": "devops",
  "security_level": "enterprise",
  "core_services": ["Azure Kubernetes Service", "Azure Container Registry"],
  "browse_tags": ["Azure", "Containers"]
}
```

## Related Documentation

- [Architecture Recommendations App](./recommendations-app.md) - Customer-facing web application
- [Architecture Scorer](./architecture-scorer.md) - Scoring engine documentation
- [Configuration Reference](../CONFIGURATION.md) - Full configuration options
