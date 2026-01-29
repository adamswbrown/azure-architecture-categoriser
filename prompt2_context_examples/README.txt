Prompt 2 Test Fixtures (v2)

This zip contains realistic application context files generated to match the output shape of AppCatContextFileCreator.py:
- Top-level JSON array containing exactly one object.
- Keys: app_overview, detected_technology_running, app_approved_azure_services, server_details, App Mod results.

Files:
- 01-java-refactor-aks.json
- 02-dotnet-replatform-appservice.json
- 03-legacy-tolerate.json
- 04-mixed-java-dotnet-partial-appmod.json (edge: mixed stack + partial App Mod)
- 05-java-replatform-partial-appmod-missing-compat.json (edge: partial/older App Mod payload)
- 06-dotnet-conflicting-signals-appmod-overrides.json (edge: conflicting signals; App Mod must override)
- 07-greenfield-cloud-native-perfect.json (greenfield-style, cloud-native)

Expected results:
- _expected_top3_from_catalog.json contains expected Top-3 architectures for each fixture.
  These are selected programmatically from the provided architecture-catalog.json using simple keyword/tag predicates.
  Treat them as "initial expectations" for PoC tests, not as a definitive oracle.
Generated at: 2026-01-29T10:32:23.091430Z
