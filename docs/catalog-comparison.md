# Catalog Comparison: Quick Build vs Full Build

This document compares the two primary catalog build options available in the Catalog Builder.

## Overview

| Attribute | Quick Build | Full Build |
|-----------|-------------|------------|
| **Total Architectures** | ~51 | ~171 |
| **Content Types** | Reference architectures only | Reference architectures + Examples + Solution Ideas |
| **Primary Use Case** | Production recommendations | Broader exploration |
| **Quality Focus** | Curated, production-ready | Includes experimental patterns |

## Build Configuration

### Quick Build
```python
allowed_topics = ['reference-architecture']
exclude_examples = True
```

### Full Build
```python
allowed_topics = ['reference-architecture', 'example-scenario', 'solution-idea']
exclude_examples = False
```

---

## Categorical Differences

### Categories Only in Full Build

| Category Type | Value | Count in Full | Notes |
|---------------|-------|---------------|-------|
| **Operating Model** | `transitional` | 9 | Organizations moving between traditional IT and DevOps |
| **Architecture Family** | `integration` | 1 | Integration-focused patterns |

### Transitional Operating Model Architectures

The "transitional" operating model only appears in example-scenario and solution-idea content:

- **example-scenario (4)**: Serverless applications, data pipelines
- **solution-idea (3)**: App Service web apps, IoT scenarios
- **other/AI-ML (2)**: AI/ML workloads, secure compute

---

## Distribution Comparisons

### Operating Models

| Model | Quick Build | Full Build |
|-------|-------------|------------|
| devops | 31 (61%) | 81 (47%) |
| sre | 15 (29%) | 60 (35%) |
| traditional_it | 5 (10%) | 21 (12%) |
| transitional | 0 (0%) | 9 (5%) |

### Security Levels

| Level | Quick Build | Full Build |
|-------|-------------|------------|
| enterprise | 31 (61%) | 90 (53%) |
| regulated | 8 (16%) | 35 (20%) |
| highly_regulated | 6 (12%) | 13 (8%) |
| basic | 6 (12%) | 33 (19%) |

### Cost Profiles

| Profile | Quick Build | Full Build |
|---------|-------------|------------|
| innovation_first | 19 (37%) | 72 (42%) |
| scale_optimized | 19 (37%) | 50 (29%) |
| balanced | 7 (14%) | 23 (13%) |
| cost_minimized | 6 (12%) | 26 (15%) |

### Workload Domains

| Domain | Quick Build | Full Build |
|--------|-------------|------------|
| infrastructure | 34 (67%) | 104 (61%) |
| integration | 7 (14%) | 14 (8%) |
| data | 4 (8%) | 19 (11%) |
| ai | 3 (6%) | 20 (12%) |
| web | 2 (4%) | 9 (5%) |
| security | 1 (2%) | 5 (3%) |

### Architecture Families

| Family | Quick Build | Full Build |
|--------|-------------|------------|
| iaas | 25 (49%) | 68 (40%) |
| paas | 11 (22%) | 37 (22%) |
| cloud_native | 9 (18%) | 32 (19%) |
| data | 4 (8%) | 30 (18%) |
| foundation | 1 (2%) | 2 (1%) |
| specialized | 1 (2%) | 1 (1%) |
| integration | 0 (0%) | 1 (1%) |

### Runtime Models

| Model | Quick Build | Full Build |
|-------|-------------|------------|
| n_tier | 22 (27%) | 60 (23%) |
| mixed | 18 (22%) | 68 (26%) |
| event_driven | 12 (15%) | 38 (15%) |
| monolith | 10 (12%) | 29 (11%) |
| microservices | 9 (11%) | 25 (10%) |
| batch | 6 (7%) | 26 (10%) |
| api | 5 (6%) | 21 (8%) |

### Availability Models

| Model | Quick Build | Full Build |
|-------|-------------|------------|
| single_region | 21 (31%) | 84 (40%) |
| zone_redundant | 20 (29%) | 47 (22%) |
| multi_region_active_passive | 18 (26%) | 57 (27%) |
| multi_region_active_active | 9 (13%) | 24 (11%) |

### Supported Treatments

| Treatment | Quick Build | Full Build |
|-----------|-------------|------------|
| replatform | 36 (28%) | 134 (29%) |
| retain | 36 (28%) | 121 (26%) |
| refactor | 26 (20%) | 96 (21%) |
| rehost | 20 (15%) | 67 (15%) |
| rebuild | 9 (7%) | 35 (8%) |
| replace | 2 (2%) | 7 (2%) |
| retire | 2 (2%) | 3 (1%) |

---

## Complexity Distribution

### Implementation Complexity

| Level | Quick Build | Full Build |
|-------|-------------|------------|
| high | 31 (61%) | 109 (64%) |
| medium | 16 (31%) | 48 (28%) |
| low | 4 (8%) | 14 (8%) |

### Operations Complexity

| Level | Quick Build | Full Build |
|-------|-------------|------------|
| high | 36 (71%) | 111 (65%) |
| medium | 12 (24%) | 51 (30%) |
| low | 3 (6%) | 9 (5%) |

---

## Catalog Quality

This is the most significant difference between the two builds.

| Quality Level | Quick Build | Full Build | Description |
|---------------|-------------|------------|-------------|
| **curated** | 42 (82%) | 42 (25%) | Manually reviewed, production-ready |
| **example_only** | 0 (0%) | 120 (70%) | Example scenarios, less rigorous |
| **ai_suggested** | 8 (16%) | 8 (5%) | AI-classified, needs review |
| **ai_enriched** | 1 (2%) | 1 (1%) | AI-enhanced metadata |

**Key Insight**: Quick Build is 82% curated content, while Full Build is 70% example-only content.

---

## Content Type Breakdown

| Content Type | Quick Build | Full Build |
|--------------|-------------|------------|
| reference-architecture | 30 | 32 |
| example-scenario | 4 | 76 |
| solution-idea | 0 | 21 |
| other | 17 | 42 |

---

## Recommendations

### Use Quick Build When:
- You want **production-ready** architecture recommendations
- Quality and curation are priorities
- You prefer **fewer, higher-confidence** matches
- Your use case aligns with standard enterprise patterns

### Use Full Build When:
- You want to **explore** a wider range of patterns
- You're looking for **inspiration** or edge cases
- Your requirements are unusual or experimental
- You want to see **example implementations** alongside reference architectures

### Custom Build:
Use the Custom Build option when you need specific filtering:
- Filter by Azure products
- Filter by specific categories
- Include/exclude specific content types
- Fine-tune for your organization's needs

---

## Technical Notes

- Catalog generation uses the Azure Architecture Center repository
- Content types are determined by the `ms.topic` frontmatter field
- Operating models are AI-classified based on content analysis
- Quality levels reflect the source and review status of each entry

---

*Generated: January 2025*
