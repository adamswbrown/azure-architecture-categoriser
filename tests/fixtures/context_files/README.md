# Sample Context Files

This directory contains sample context files for testing and demonstrating
the Azure Architecture Recommender.

## Scenarios

| File | Name | Treatment | Expected Confidence |
|------|------|-----------|---------------------|
| `01-java-refactor-aks.json` | Java Spring Boot Refactor to AKS | Refactor | high |
| `02-dotnet-replatform-appservice.json` | .NET Core Replatform to App Service | Replatform | high |
| `03-legacy-tolerate.json` | Legacy VB6 Application - Tolerate | Tolerate | medium |
| `04-mixed-java-dotnet-partial-appmod.json` | Mixed Java/.NET with Partial Modernization | Refactor | medium |
| `07-greenfield-cloud-native-perfect.json` | Greenfield Cloud-Native Application | Rebuild | very_high |
| `09-rehost-vm-lift-shift.json` | VM Lift-and-Shift Migration | Rehost | high |
| `13-highly-regulated-healthcare.json` | Healthcare Application (HIPAA Compliant) | Replatform | high |
| `17-cost-minimized-startup.json` | Startup MVP (Cost Optimized) | Replatform | high |
| `18-innovation-first-ai-ml.json` | AI/ML Innovation Platform | Rebuild | high |
| `19-appmod-blockers-mainframe.json` | Mainframe COBOL Application | Retain | low |
| `14-multi-region-active-active.json` | Mission-Critical Multi-Region | Refactor | high |
| `15-traditional-it-erp.json` | Traditional IT - SAP ERP | Replatform | high |

## Usage

These files can be used with:

1. **Recommendations App** - Upload any file to get architecture recommendations
2. **CLI Scorer** - `architecture-scorer score --context <file>.json`
3. **Testing** - Automated tests use these as fixtures

## Regenerating

To regenerate these files:

```bash
# macOS/Linux
./bin/generate-sample-data.sh

# Windows PowerShell
.\bin\generate-sample-data.ps1

# Or directly with Python
python3 tests/generate_sample_data.py
```

### Generator Options

```bash
# List all available scenarios
./bin/generate-sample-data.sh --list

# Generate only the index file
./bin/generate-sample-data.sh --index-only

# Generate a specific scenario
./bin/generate-sample-data.sh --scenario 01-java-refactor-aks

# Generate to a custom directory
./bin/generate-sample-data.sh --output-dir ./my-samples
```

## Adding New Scenarios

Edit `tests/generate_sample_data.py` and add a new `Scenario` object to the
`SCENARIOS` list. Run the generator to create the file.

## Schema

Each context file follows the Dr. Migrate output format:

```json
[{
  "app_overview": [{
    "application": "AppName",
    "app_type": "Web Application",
    "business_crtiticality": "High",
    "treatment": "Refactor"
  }],
  "detected_technology_running": ["Java 11", "Spring Boot"],
  "app_approved_azure_services": [{
    "Java": "Azure Kubernetes Service"
  }],
  "server_details": [...],
  "App Mod results": [...]
}]
```
