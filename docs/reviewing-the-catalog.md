# Reviewing the Architecture Catalog

This guide explains how to review and validate the architecture catalog to ensure it meets your organization's needs.

## Overview

The architecture catalog is a JSON file containing structured metadata about Azure architectures. Before using it for recommendations, you should review:

1. **Coverage** - Are the architectures you need included?
2. **Quality** - Is the metadata accurate and complete?
3. **Relevance** - Are the included architectures appropriate for your use cases?

## Viewing the Catalog

### Option 1: CLI Inspection (Recommended)

```bash
# View overall statistics
catalog-builder stats --catalog architecture-catalog.json

# List all architectures
catalog-builder inspect --catalog architecture-catalog.json

# Filter by family
catalog-builder inspect --catalog architecture-catalog.json --family cloud_native

# View a specific architecture
catalog-builder inspect --catalog architecture-catalog.json --id <architecture-id>
```

### Option 2: GUI Browser

```bash
# Launch the catalog builder GUI
./bin/start-catalog-builder-gui.sh
```

Navigate to the **Build Catalog** tab, generate a catalog, then browse entries in the results panel.

### Option 3: Direct JSON Inspection

```bash
# Pretty-print the catalog
cat architecture-catalog.json | python -m json.tool | less

# Count entries
cat architecture-catalog.json | python -c "import json,sys; print(len(json.load(sys.stdin)))"

# Extract just names
cat architecture-catalog.json | python -c "import json,sys; [print(a['name']) for a in json.load(sys.stdin)]"
```

## What to Review

### 1. Catalog Statistics

Run `catalog-builder stats` and check:

| Metric | What to Look For |
|--------|------------------|
| **Total Architectures** | ~50 for reference-only, ~230 for all types |
| **Quality Distribution** | Higher % of "curated" = better metadata |
| **Family Distribution** | Should cover your workload types |
| **Top Services** | Should include services your organization uses |

**Example output:**
```
Catalog Statistics
==================
Total Architectures: 52
Quality Distribution:
  - curated: 38 (73%)
  - ai_enriched: 10 (19%)
  - ai_suggested: 4 (8%)

Family Distribution:
  - cloud_native: 18
  - data: 12
  - web: 8
  ...
```

### 2. Individual Entry Review

For each architecture entry, verify:

#### Identity Fields
| Field | Check |
|-------|-------|
| `name` | Clear, descriptive title |
| `description` | Accurate summary of the architecture |
| `learn_url` | Links to correct Microsoft Learn page |
| `pattern_name` | Normalized, searchable pattern name |

#### Classification Fields
| Field | Check |
|-------|-------|
| `family` | Correct architectural family |
| `workload_domain` | Matches the primary use case |
| `catalog_quality` | Reflects confidence in metadata |

#### Expectations Fields
| Field | Check |
|-------|-------|
| `expected_runtime_models` | Matches the architecture's design |
| `expected_characteristics` | Accurately describes requirements |
| `supported_treatments` | Lists valid migration approaches |
| `availability_models` | Matches documented capabilities |
| `security_level` | Reflects compliance requirements |
| `operating_model_required` | Matches operational complexity |

#### Services Fields
| Field | Check |
|-------|-------|
| `core_services` | Lists essential Azure services |
| `supporting_services` | Lists optional/supporting services |

### 3. Quality Level Meanings

| Level | Confidence | Action |
|-------|------------|--------|
| **curated** | High | Trust as-is |
| **ai_enriched** | Medium-High | Spot-check key fields |
| **ai_suggested** | Medium | Review all classification fields |
| **example_only** | Low | Review carefully, may not be prescriptive |

## Review Checklist

### Quick Review (5 minutes)

- [ ] Run `catalog-builder stats` and verify counts
- [ ] Check quality distribution (aim for >50% curated)
- [ ] Verify top services include your organization's primary services
- [ ] Spot-check 3-5 random entries for accuracy

### Thorough Review (30 minutes)

- [ ] Complete quick review
- [ ] Review all `ai_suggested` entries (lowest confidence)
- [ ] Verify `learn_url` links work for 10+ entries
- [ ] Check that key architectures for your use cases are included
- [ ] Review `supported_treatments` for migration-focused entries
- [ ] Verify `availability_models` for high-availability architectures

### Deep Review (2+ hours)

- [ ] Complete thorough review
- [ ] Review every entry in your primary workload domains
- [ ] Cross-reference with Microsoft Learn documentation
- [ ] Validate `core_services` lists against actual architecture diagrams
- [ ] Document any corrections needed
- [ ] Test recommendations with sample context files

## Common Issues to Look For

### Missing Architectures

**Symptom:** Expected architecture not in catalog

**Causes:**
- Filtered out by topic (only reference architectures by default)
- Missing `ms.topic` metadata in source
- Excluded by detection heuristics

**Solution:**
```bash
# Include example scenarios and solution ideas
catalog-builder build-catalog \
  --repo-path ./architecture-center \
  --topic reference-architecture \
  --topic example-scenario \
  --topic solution-idea \
  --out catalog-with-examples.json
```

### Incorrect Classification

**Symptom:** Architecture has wrong `family` or `workload_domain`

**Causes:**
- AI classification error
- Ambiguous source content
- Multi-domain architecture

**Impact:** May affect scoring accuracy for that architecture

**Note:** Classification is extracted from source metadata or inferred by AI. Manual overrides are not currently supported but could be added via catalog post-processing.

### Missing Services

**Symptom:** `core_services` list incomplete

**Causes:**
- Service names not normalized
- Services mentioned in diagrams but not text
- Service aliases not recognized

**Impact:** Service-based matching may be less accurate

### Broken Learn URLs

**Symptom:** `learn_url` returns 404

**Causes:**
- Page moved or renamed
- URL construction error
- Temporary Microsoft Learn issue

**Verification:**
```bash
# Test URLs (sample 10 entries)
cat architecture-catalog.json | python -c "
import json, sys, requests
catalog = json.load(sys.stdin)
for arch in catalog[:10]:
    url = arch.get('learn_url', '')
    if url:
        try:
            r = requests.head(url, timeout=5, allow_redirects=True)
            status = '✓' if r.status_code == 200 else f'✗ {r.status_code}'
        except:
            status = '✗ Error'
        print(f'{status} {arch[\"name\"][:50]}')"
```

## Validating Recommendations

After reviewing the catalog, test it with the recommendations app:

```bash
# Start the recommendations app
./bin/start-recommendations-app.sh
```

1. Upload a sample context file from `examples/context_files/`
2. Review the recommendations - do they make sense?
3. Check that scores align with expectations
4. Answer clarification questions and verify re-scoring improves results

## Updating the Catalog

If you find issues, you have several options:

### Regenerate with Different Filters

```bash
# More inclusive (more architectures, lower average quality)
catalog-builder build-catalog \
  --repo-path ./architecture-center \
  --topic reference-architecture \
  --topic example-scenario \
  --out catalog-inclusive.json

# More selective (fewer architectures, higher quality)
catalog-builder build-catalog \
  --repo-path ./architecture-center \
  --require-yml \
  --out catalog-curated-only.json
```

### Update Source Repository

```bash
cd ./architecture-center
git pull origin main
```

Then regenerate the catalog to pick up new/updated architectures.

### Post-Process the Catalog

For advanced users, you can modify the JSON directly:

```python
import json

# Load catalog
with open('architecture-catalog.json') as f:
    catalog = json.load(f)

# Make corrections
for arch in catalog:
    if arch['architecture_id'] == 'some-specific-id':
        arch['family'] = 'cloud_native'  # Correct classification

# Save updated catalog
with open('architecture-catalog-corrected.json', 'w') as f:
    json.dump(catalog, f, indent=2)
```

## Review Frequency

| Trigger | Action |
|---------|--------|
| Initial setup | Full thorough review |
| Monthly | Quick review + check for new architectures |
| Azure Architecture Center update | Regenerate and quick review |
| Before production deployment | Thorough review |
| After recommendation quality issues | Deep review of affected areas |

## Related Documentation

- [Catalog Builder](./catalog-builder.md) - How to generate catalogs
- [Architecture Scorer](./architecture-scorer.md) - How recommendations are scored
- [Recommendations App](./recommendations-app.md) - Customer-facing application
