---
layout: default
title: Architecture Categorization Guide
---

# Architecture Categorization Guide

This document explains how architectures are categorized in the catalog, where the data comes from, and how to validate classifications during manual review.

## Overview

The categorization system extracts and classifies architecture metadata from the Azure Architecture Center documentation. Each architecture receives classifications across multiple dimensions:

| Dimension | Purpose | Example Values |
|-----------|---------|----------------|
| **family** | Primary architectural pattern | iaas, paas, cloud_native, data |
| **workload_domain** | Business domain | web, data, ai, infrastructure |
| **supported_treatments** | Migration strategies | rehost, replatform, refactor |
| **operating_model_required** | Team capability needed | traditional_it, devops, sre |
| **security_level** | Compliance requirements | basic, enterprise, regulated |
| **cost_profile** | Cost characteristics | cost_minimized, balanced, scale_optimized |

## Data Sources

### Priority 1: YamlMime:Architecture Files (Most Reliable)

Each architecture in the Azure Architecture Center has a paired `.yml` file containing curated metadata. These files start with `### YamlMime:Architecture` and contain:

```yaml
### YamlMime:Architecture
name: "Architecture Name"
summary: "Description of the architecture"
products:
  - azure-kubernetes-service
  - azure-container-registry
azureCategories:
  - containers
  - compute
metadata:
  ms.topic: reference-architecture
  ms.custom: arb-containers       # <-- Key classification hint
  ms.collection: migration        # <-- Treatment hint
```

**Key fields extracted:**
- `products` - Azure service identifiers
- `azureCategories` - High-level categorization
- `metadata.ms.topic` - Document type (reference-architecture, example-scenario)
- `metadata.ms.custom` - Contains `arb-*` values for family classification
- `metadata.ms.collection` - Contains treatment hints (migration, onprem-to-azure)

### Priority 2: Azure Services (Reliable)

Services detected from `products` field and content analysis are used to infer family:

| Services Detected | Inferred Family |
|-------------------|-----------------|
| Azure Kubernetes Service, Container Apps | cloud_native |
| Azure Virtual Machines | iaas |
| Azure App Service, Functions | paas |
| Azure Synapse, Data Factory | data |
| ExpressRoute, VPN Gateway, Load Balancer | iaas |

### Priority 3: Content Analysis (Fallback)

Keywords in the document content are used when yml metadata is insufficient:

- Container/microservices keywords → cloud_native
- VM/infrastructure keywords → iaas
- Database/analytics keywords → data

---

## Family Classification

### Classification Priority Order

```
1. ms.custom arb-* values     → CURATED confidence
2. ms.custom e2e-* values     → CURATED confidence
3. Service inference          → AI_SUGGESTED confidence
4. Category inference         → AI_SUGGESTED confidence
5. Content analysis           → AI_SUGGESTED confidence (lowest reliability)
```

### arb-* Value Mappings (Highest Priority)

The `ms.custom` field may contain `arb-*` prefixed values that directly map to families:

| ms.custom Value | Family | Confidence |
|-----------------|--------|------------|
| `arb-web` | paas | curated |
| `arb-data` | data | curated |
| `arb-containers` | cloud_native | curated |
| `arb-hybrid` | iaas | curated |
| `arb-aiml` | data | curated |

**Example:** An architecture with `ms.custom: arb-containers` will always be classified as `cloud_native` with `curated` confidence.

### Additional Custom Mappings

| ms.custom Value | Family | Rationale |
|-----------------|--------|-----------|
| `e2e-hybrid` | iaas | Hybrid connectivity typically involves VMs |

### Category-Based Inference

When no arb-* values exist, `azureCategories` can suggest family:

| Azure Category | Inferred Family |
|----------------|-----------------|
| `hybrid` | iaas |
| `identity` | iaas |
| `containers` | cloud_native |

### Service-Based Inference

If no metadata mappings match, services are used:

| Service Pattern | Family Boost | Score |
|-----------------|--------------|-------|
| kubernetes, container | cloud_native | +3 |
| virtual machine | iaas | +2 |
| app service, functions | paas | +2 |
| synapse, data factory | data | +2 |
| expressroute, vpn gateway, load balancer | iaas | +2 |

The highest-scoring family wins.

---

## Workload Domain Classification

### Data Source Priority

```
1. azureCategories from yml    → CURATED confidence
2. Content keyword analysis    → AI_SUGGESTED confidence
```

### Category to Domain Mappings

| Azure Category | Workload Domain |
|----------------|-----------------|
| web | web |
| ai-machine-learning | ai |
| analytics | data |
| databases | data |
| compute | infrastructure |
| containers | infrastructure |
| networking | infrastructure |
| hybrid | infrastructure |
| integration | integration |
| security | security |
| identity | security |
| storage | data |

---

## Supported Treatments Classification

Treatments indicate which migration strategies an architecture supports.

### Data Source Priority

```
1. ms.collection values        → yml_metadata source
2. Service-based inference     → service_inference source
3. Family-based hints          → family_heuristic source
```

### ms.collection Mappings

| ms.collection Value | Treatment Boost |
|---------------------|-----------------|
| `migration` | rehost +2, replatform +2 |
| `onprem-to-azure` | rehost +1.5, replatform +1.5 |

### Service-Based Treatment Inference

| Services | Treatment Boost |
|----------|-----------------|
| Virtual Machines | rehost +2, retain +1 |
| Kubernetes, Container Apps | refactor +2, rebuild +1 |
| Managed databases (SQL, Cosmos) | replatform +2 |
| ExpressRoute, Arc, VPN Gateway | retain +2 |
| App Service, Functions | replatform +1.5 |

### Family-Based Treatment Hints

| Family | Default Treatments |
|--------|-------------------|
| iaas | rehost, replatform, retain |
| paas | replatform, refactor |
| cloud_native | refactor, rebuild |
| data | replatform, refactor |

---

## Operating Model Classification

The `operating_model_required` field indicates what team capability is needed.

### Hierarchy (Lowest to Highest)

```
traditional_it → transitional → devops → sre
```

### Inference Sources

| Signal | Operating Model |
|--------|-----------------|
| Cloud-native family | devops |
| Microservices runtime | devops |
| Multi-region active-active | sre |
| PaaS family | transitional |
| IaaS family | traditional_it |
| DevOps keywords in content | devops |

**Important:** Operating model is derived from content complexity, NOT directly from family. An IAAS architecture can require SRE if it has complex HA/DR requirements.

---

## Confidence Levels

### Classification Confidence

| Level | Meaning | Source |
|-------|---------|--------|
| **curated** | Derived from explicit yml metadata (arb-*, e2e-*) | yml_metadata |
| **ai_suggested** | Inferred from services, categories, or content | service_inference, category_inference, content_analysis |
| **manual_required** | Could not determine, needs human review | none |

### Catalog Quality

| Level | Meaning |
|-------|---------|
| **curated** | High-quality reference architecture with complete metadata |
| **ai_enriched** | Good metadata with some AI-suggested fields |
| **ai_suggested** | Most fields AI-suggested, needs review |
| **example_only** | Example scenario, not a prescriptive reference |

---

## Current Catalog Statistics

As of the last generation:

### Family Classification Sources

| Source | Count | Confidence |
|--------|-------|------------|
| yml_metadata (arb-*, e2e-*) | 29 | curated |
| service_inference | 13 | ai_suggested |
| category_inference | 1 | ai_suggested |
| content_analysis | 0 | ai_suggested |

### Family Distribution

| Family | Count |
|--------|-------|
| iaas | 25 |
| paas | 9 |
| cloud_native | 4 |
| data | 4 |
| foundation | 1 |

---

## Manual Review Checklist

### For Each Architecture, Verify:

#### 1. Family Classification
- [ ] Check `family_confidence.source` - is it `yml_metadata` or inferred?
- [ ] If `yml_metadata`: Trust it (derived from Microsoft's arb-* values)
- [ ] If `service_inference`: Verify services match the inferred family
- [ ] If `content_analysis`: Review carefully - lowest confidence

#### 2. Operating Model
- [ ] Does the operating model match the architecture's complexity?
- [ ] IAAS + simple networking = `traditional_it` is correct
- [ ] IAAS + multi-region HA/DR = `sre` may be correct
- [ ] Cloud-native + containers = `devops` is expected

#### 3. Supported Treatments
- [ ] Do treatments align with the architecture's purpose?
- [ ] Hybrid architectures should support `retain`
- [ ] Migration architectures should support `rehost`, `replatform`
- [ ] Cloud-native should support `refactor`, `rebuild`

#### 4. Services
- [ ] Are `core_services` the essential services for this pattern?
- [ ] Are `supporting_services` optional/complementary?
- [ ] Are any key services missing?

### Red Flags to Look For

| Issue | What to Check |
|-------|---------------|
| IAAS family but no VM services | May be misclassified |
| cloud_native family but no container services | May be misclassified |
| devops/sre operating model for simple architecture | May be over-classified |
| traditional_it for complex HA architecture | May be under-classified |
| Empty treatments list | Classification may have failed |
| `content_analysis` source | Lowest confidence, review carefully |

---

## Specific Architecture Review

### Architectures Using yml_metadata (29 total)

These have the highest confidence. Verify:
- The arb-* or e2e-* value makes sense for the architecture
- Services align with the inferred family

### Architectures Using service_inference (13 total)

These were classified based on Azure services. Verify:
- Services detected are actually core to the architecture
- Family inference makes sense given those services

### Architectures Using category_inference (1 total)

This was classified based on Azure category. Verify:
- The architecture fits the category-based classification

---

## Files Reference

### Classification Logic
- [classifier.py](../src/catalog_builder/classifier.py) - Main classification logic
  - `ARB_TO_FAMILY` - arb-* value mappings (line ~50)
  - `CUSTOM_TO_FAMILY` - e2e-* value mappings (line ~59)
  - `CATEGORY_TO_FAMILY` - Category mappings (line ~64)
  - `_suggest_family()` - Family classification method (line ~205)

### Metadata Extraction
- [parser.py](../src/catalog_builder/parser.py) - YML parsing logic
  - `_parse_architecture_yml()` - Extracts ms.custom, ms.collection (line ~289)
  - `ArchitectureMetadata` dataclass - Stores extracted metadata (line ~187)

### Configuration
- [config.py](../src/catalog_builder/config.py) - Configurable keywords and thresholds
  - `family_keywords` - Keywords for family detection
  - `treatment_keywords` - Keywords for treatment detection

---

## Troubleshooting

### "Why is this architecture classified as X?"

1. Check `family_confidence.source` in the catalog JSON
2. If `yml_metadata`: Look for arb-* or e2e-* in the source yml file
3. If `service_inference`: Check which services triggered the classification
4. If `category_inference`: Check azureCategories in the source yml
5. If `content_analysis`: Classification was based on content keywords

### "Why does this IAAS architecture require devops?"

Operating model is derived from **content complexity**, not family:
- Multi-region deployments → SRE
- Microservices patterns → DevOps
- CI/CD requirements → DevOps
- Simple VM deployments → Traditional IT

### "Why are there only 4 cloud_native architectures?"

Many container-based architectures also use hybrid networking (VPN, ExpressRoute) and are classified as IAAS because:
1. They have `e2e-hybrid` in ms.custom, OR
2. They use networking services that boost IAAS score

This is intentional - these are hybrid architectures that happen to use containers, not pure cloud-native patterns.

---

## Contact

For questions about categorization logic or to report classification issues, contact the catalog maintainer or open an issue in the repository.
