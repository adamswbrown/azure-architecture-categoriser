# Configuration Reference

This document describes all configurable settings in the Azure Architecture Catalog Builder and where to modify them.

---

## Table of Contents

1. [Detection Settings](#detection-settings)
2. [Classification Keywords](#classification-keywords)
3. [Service Normalization](#service-normalization)
4. [URL Configuration](#url-configuration)
5. [Detection Thresholds](#detection-thresholds)

---

## Detection Settings

**File:** [src/catalog_builder/detector.py](src/catalog_builder/detector.py)

### Include Folders

Folders that are scanned for architecture content. Files in these folders get a +0.3 confidence boost.

```python
# detector.py:24-45
INCLUDE_FOLDERS = [
    'docs/example-scenario',
    'docs/web-apps',
    'docs/data',
    'docs/integration',
    'docs/ai-ml',
    'docs/databases',
    'docs/iot',
    'docs/microservices',
    'docs/mobile',
    'docs/networking',
    'docs/security',
    'docs/solution-ideas',
    'docs/reference-architectures',
    'docs/hybrid',
    'docs/aws-professional',
    'docs/gcp-professional',
    'docs/oracle-azure',
    'docs/sap',
    'docs/high-availability',
    'docs/serverless',
]
```

### Exclude Folders

Folders that are never scanned (conceptual content, templates, etc.).

```python
# detector.py:48-60
EXCLUDE_FOLDERS = [
    'docs/guide',
    'docs/best-practices',
    'docs/patterns',
    'docs/antipatterns',
    'docs/framework',
    'docs/icons',
    'docs/includes',
    'docs/resources',
    'docs/browse',
    '_themes',
    '_shared',
]
```

### Exclude Files

Specific filenames that are always skipped.

```python
# detector.py:63-69
EXCLUDE_FILES = [
    'index.md',
    'toc.yml',
    'toc.md',
    'readme.md',
    'changelog.md',
]
```

### Architecture Section Names

Section headings that indicate architecture content (+0.2 confidence).

```python
# detector.py:72-83
ARCHITECTURE_SECTIONS = [
    'architecture',
    'components',
    'diagram',
    'solution architecture',
    'reference architecture',
    'architectural approach',
    'design',
    'workflow',
    'data flow',
    'dataflow',
]
```

### Architecture Keywords

Regex patterns that indicate architecture content (+0.2 confidence).

```python
# detector.py:86-97
ARCHITECTURE_KEYWORDS = [
    r'reference\s+architecture',
    r'baseline\s+architecture',
    r'solution\s+idea',
    r'architecture\s+pattern',
    r'architectural\s+design',
    r'this\s+architecture',
    r'the\s+architecture',
    r'architecture\s+diagram',
    r'components\s+of\s+this',
    r'azure\s+architecture',
]
```

### Diagram Patterns

Regex patterns to identify architecture diagram files (+0.3 confidence).

```python
# detector.py:100-106
DIAGRAM_PATTERNS = [
    r'.*architecture.*\.(svg|png)$',
    r'.*diagram.*\.(svg|png)$',
    r'.*flow.*\.(svg|png)$',
    r'.*-arch\.(svg|png)$',
    r'.*\.svg$',
]
```

---

## Classification Keywords

**File:** [src/catalog_builder/classifier.py](src/catalog_builder/classifier.py)

### Workload Domain Keywords

Keywords used to suggest the `workload_domain` field.

```python
# classifier.py:27-59
DOMAIN_KEYWORDS = {
    WorkloadDomain.WEB: [
        'web app', 'website', 'frontend', 'spa', 'single page',
        'web application', 'web service', 'web api', 'blazor',
        'asp.net', 'react', 'angular', 'vue', 'node.js',
    ],
    WorkloadDomain.DATA: [
        'data warehouse', 'data lake', 'analytics', 'big data',
        'etl', 'data pipeline', 'olap', 'reporting', 'bi ',
        'business intelligence', 'data platform', 'synapse',
        'databricks', 'data factory', 'hdinsight',
    ],
    WorkloadDomain.INTEGRATION: [
        'integration', 'api gateway', 'message', 'queue', 'event',
        'service bus', 'event hub', 'event grid', 'logic app',
        'b2b', 'edi', 'middleware', 'esb', 'ipaa',
    ],
    WorkloadDomain.SECURITY: [
        'security', 'identity', 'authentication', 'authorization',
        'zero trust', 'firewall', 'waf', 'ddos', 'encryption',
        'key vault', 'secret', 'certificate', 'compliance',
    ],
    WorkloadDomain.AI: [
        'machine learning', 'ml ', 'ai ', 'artificial intelligence',
        'cognitive', 'nlp', 'computer vision', 'deep learning',
        'neural', 'openai', 'gpt', 'llm', 'chatbot', 'bot ',
    ],
    WorkloadDomain.INFRASTRUCTURE: [
        'infrastructure', 'network', 'hybrid', 'vpn', 'expressroute',
        'virtual network', 'vnet', 'dns', 'load balancer', 'firewall',
        'hub and spoke', 'landing zone', 'governance',
    ],
}
```

### Architecture Family Keywords

Keywords used to suggest the `family` field.

```python
# classifier.py:62-91
FAMILY_KEYWORDS = {
    ArchitectureFamily.FOUNDATION: [
        'landing zone', 'foundation', 'baseline', 'governance',
        'enterprise scale', 'caf ', 'cloud adoption',
    ],
    ArchitectureFamily.IAAS: [
        'virtual machine', 'vm ', 'iaas', 'lift and shift',
        'vm scale set', 'vmss', 'availability set',
    ],
    ArchitectureFamily.PAAS: [
        'app service', 'paas', 'platform as a service',
        'azure sql', 'cosmos db', 'managed service',
    ],
    ArchitectureFamily.CLOUD_NATIVE: [
        'kubernetes', 'aks', 'container', 'microservice',
        'cloud native', 'serverless', 'function', 'cloud-native',
    ],
    ArchitectureFamily.DATA: [
        'data platform', 'data warehouse', 'data lake',
        'analytics', 'synapse', 'databricks', 'data mesh',
    ],
    ArchitectureFamily.INTEGRATION: [
        'integration', 'api management', 'logic app',
        'service bus', 'event-driven', 'messaging',
    ],
    ArchitectureFamily.SPECIALIZED: [
        'sap', 'oracle', 'mainframe', 'hpc', 'high performance',
        'gaming', 'media', 'iot', 'digital twin',
    ],
}
```

### Runtime Model Keywords

Keywords used to suggest the `expected_runtime_models` field.

```python
# classifier.py:94-118
RUNTIME_KEYWORDS = {
    RuntimeModel.MICROSERVICES: [
        'microservice', 'micro-service', 'distributed service',
        'service mesh', 'sidecar', 'dapr',
    ],
    RuntimeModel.EVENT_DRIVEN: [
        'event-driven', 'event driven', 'event sourcing', 'cqrs',
        'pub/sub', 'publish subscribe', 'reactive',
    ],
    RuntimeModel.API: [
        'rest api', 'graphql', 'api-first', 'api gateway',
        'web api', 'api management',
    ],
    RuntimeModel.N_TIER: [
        'n-tier', 'three-tier', '3-tier', 'multi-tier',
        'presentation layer', 'business layer', 'data layer',
    ],
    RuntimeModel.BATCH: [
        'batch processing', 'batch job', 'scheduled job',
        'etl', 'data pipeline', 'nightly job',
    ],
    RuntimeModel.MONOLITH: [
        'monolith', 'single application', 'traditional app',
    ],
}
```

### Availability Keywords

Keywords used to suggest the `availability_models` field.

```python
# classifier.py:121-134
AVAILABILITY_KEYWORDS = {
    AvailabilityModel.MULTI_REGION_ACTIVE_ACTIVE: [
        'active-active', 'multi-region active', 'global distribution',
        'geo-replication', 'global load balancing',
    ],
    AvailabilityModel.MULTI_REGION_ACTIVE_PASSIVE: [
        'active-passive', 'disaster recovery', 'dr region',
        'failover region', 'backup region', 'geo-redundant',
    ],
    AvailabilityModel.ZONE_REDUNDANT: [
        'zone redundant', 'availability zone', 'zone-redundant',
        'across zones', 'zonal',
    ],
}
```

---

## Service Normalization

**File:** [src/catalog_builder/parser.py](src/catalog_builder/parser.py)

### Azure Service Name Mappings

Maps common abbreviations and variants to canonical Azure service names.

```python
# parser.py:170-206
normalizations = {
    'aks': 'Azure Kubernetes Service',
    'vm': 'Azure Virtual Machines',
    'vms': 'Azure Virtual Machines',
    'sql database': 'Azure SQL Database',
    'cosmos db': 'Azure Cosmos DB',
    'app service': 'Azure App Service',
    'functions': 'Azure Functions',
    'blob storage': 'Azure Blob Storage',
    'key vault': 'Azure Key Vault',
    'api management': 'Azure API Management',
    'front door': 'Azure Front Door',
    'application gateway': 'Azure Application Gateway',
    'load balancer': 'Azure Load Balancer',
    'event hub': 'Azure Event Hubs',
    'event hubs': 'Azure Event Hubs',
    'service bus': 'Azure Service Bus',
    'event grid': 'Azure Event Grid',
    'container apps': 'Azure Container Apps',
    'container instances': 'Azure Container Instances',
    'redis cache': 'Azure Cache for Redis',
    'cache for redis': 'Azure Cache for Redis',
    'active directory': 'Microsoft Entra ID',
    'entra id': 'Microsoft Entra ID',
    'monitor': 'Azure Monitor',
    'application insights': 'Application Insights',
    'log analytics': 'Azure Log Analytics',
    'data factory': 'Azure Data Factory',
    'synapse': 'Azure Synapse Analytics',
    'databricks': 'Azure Databricks',
    'machine learning': 'Azure Machine Learning',
    'openai': 'Azure OpenAI Service',
    'cognitive services': 'Azure Cognitive Services',
    'logic apps': 'Azure Logic Apps',
    'signalr': 'Azure SignalR Service',
}
```

### Azure Service Detection Patterns

Regex patterns used to find Azure services in content.

```python
# parser.py:124-139
azure_patterns = [
    r'Azure\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
    r'(App\s+Service|Functions?|Cosmos\s+DB|SQL\s+Database)',
    r'(Blob\s+Storage|Queue\s+Storage|Table\s+Storage)',
    r'(Event\s+Hub|Service\s+Bus|Event\s+Grid)',
    r'(Virtual\s+Machine|VM\s+Scale\s+Set)',
    r'(Kubernetes\s+Service|AKS|Container\s+Instances|Container\s+Apps)',
    r'(API\s+Management|Front\s+Door|Application\s+Gateway|Load\s+Balancer)',
    r'(Key\s+Vault|Active\s+Directory|Entra\s+ID)',
    r'(Monitor|Log\s+Analytics|Application\s+Insights)',
    r'(Data\s+Factory|Synapse|Databricks|Data\s+Lake)',
    r'(Cognitive\s+Services|OpenAI|Machine\s+Learning)',
    r'(Redis\s+Cache|Cache\s+for\s+Redis)',
    r'(SignalR|Notification\s+Hubs)',
    r'(Logic\s+Apps|Power\s+Automate)',
]
```

---

## URL Configuration

**File:** [src/catalog_builder/extractor.py](src/catalog_builder/extractor.py)

### Microsoft Learn Base URL

Base URL for generating Learn documentation links.

```python
# extractor.py:17
LEARN_BASE_URL = "https://learn.microsoft.com/en-us/azure/architecture"
```

---

## Detection Thresholds

**File:** [src/catalog_builder/detector.py](src/catalog_builder/detector.py)

### Confidence Scoring

| Signal | Confidence Boost |
|--------|-----------------|
| In included folder | +0.3 |
| Has architecture diagrams | +0.3 |
| Has architecture sections | +0.2 |
| Contains architecture keywords | +0.2 |
| Frontmatter indicates architecture | +0.1 |

### Detection Threshold

A document is classified as an architecture if:

```python
# detector.py:174
is_architecture = score >= 0.4 and len(reasons) >= 2
```

- Minimum confidence score: **0.4**
- Minimum number of matching signals: **2**

---

## How to Modify Settings

1. **Edit the source files** directly in `src/catalog_builder/`
2. **Reinstall the package**: `pip install -e .`
3. **Rebuild the catalog**: `catalog-builder build-catalog --repo-path <path> --out catalog.json`

### Example: Add a new include folder

```python
# In detector.py, add to INCLUDE_FOLDERS:
INCLUDE_FOLDERS = [
    ...
    'docs/my-new-folder',
]
```

### Example: Add a new service normalization

```python
# In parser.py, add to normalizations dict:
normalizations = {
    ...
    'my service': 'Azure My Service',
}
```

### Example: Add a new classification keyword

```python
# In classifier.py, add to appropriate KEYWORDS dict:
DOMAIN_KEYWORDS = {
    WorkloadDomain.AI: [
        ...
        'my new ai keyword',
    ],
}
```

---

## Manual-Only Fields

These fields cannot be auto-detected and must be set manually by editing the output JSON:

| Field | Description |
|-------|-------------|
| `supported_treatments` | retire, tolerate, rehost, replatform, refactor, replace |
| `supported_time_categories` | tolerate, migrate, invest, eliminate |
| `operating_model_required` | traditional_it, transitional, devops, sre |
| `not_suitable_for` | Exclusion rules for the architecture |
| `cost_profile` | cost_minimized, balanced, scale_optimized, innovation_first |
| `security_level` | basic, enterprise, regulated, highly_regulated |
