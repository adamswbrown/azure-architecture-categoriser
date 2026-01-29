# Azure Architecture Recommender - Project State

## Current Phase
**Phase 3: Customer-Facing App & Documentation - COMPLETE**

## Status

### Catalog Builder
- [x] Project structure created
- [x] Catalog schema defined
- [x] Markdown parser implemented
- [x] Architecture detection heuristics implemented
- [x] Metadata extraction implemented
- [x] AI-assisted classification implemented
- [x] CLI built and tested
- [x] Full integration test passed
- [x] Streamlit GUI implemented
- [x] Learn URLs working correctly

### Architecture Scorer
- [x] Context normalization (Phase 1)
- [x] Intent derivation (Phase 2)
- [x] Clarification questions (Phase 3)
- [x] Architecture matching (Phase 4)
- [x] Network exposure question (always asked)
- [x] 25 test context files covering all scenarios

### Recommendations App (NEW)
- [x] 3-step wizard flow (Upload → Questions → Results)
- [x] File validation with user-friendly errors
- [x] Application summary display
- [x] Interactive clarification questions
- [x] Results display with recommendation cards
- [x] Architecture diagram images (from catalog)
- [x] PDF report generation with reportlab
- [x] JSON export
- [x] Light theme with Azure branding
- [x] Session state management

### Documentation (NEW)
- [x] Separated docs for each component
- [x] docs/catalog-builder.md
- [x] docs/recommendations-app.md
- [x] docs/architecture-scorer.md
- [x] Main README refactored as overview with navigation

## Architecture Decisions

### Technology Stack
- Python 3.11+
- Click for CLI
- Pydantic for schema validation
- PyYAML for frontmatter parsing
- Rich for terminal output
- GitPython for git metadata
- Streamlit for GUI and Recommendations App
- reportlab for PDF generation

### Project Structure
```
azure-architecture-categoriser-/
├── src/
│   ├── catalog_builder/              # Catalog generation
│   │   ├── cli.py, parser.py, detector.py
│   │   ├── extractor.py, classifier.py
│   │   ├── schema.py, catalog.py, config.py
│   ├── architecture_scorer/          # Architecture scoring
│   │   ├── cli.py, scorer.py, schema.py
│   │   ├── normalizer.py, intent_deriver.py
│   │   ├── question_generator.py, matcher.py
│   ├── catalog_builder_gui/          # Catalog Builder GUI
│   │   ├── app.py, state/
│   │   └── components/
│   └── architecture_recommendations_app/  # Customer App (NEW)
│       ├── app.py
│       ├── components/
│       │   ├── upload_section.py
│       │   ├── results_display.py
│       │   ├── questions_section.py
│       │   └── pdf_generator.py
│       ├── state/session_state.py
│       ├── utils/validation.py
│       └── .streamlit/config.toml
├── docs/                             # Component documentation (NEW)
│   ├── catalog-builder.md
│   ├── recommendations-app.md
│   └── architecture-scorer.md
├── tests/
│   ├── test_catalog_builder.py
│   ├── test_architecture_scorer.py
│   └── context_files/
├── .streamlit/config.toml            # Theme configuration
├── pyproject.toml
├── README.md, CONFIGURATION.md
├── state.md, worklog.md
└── architecture-catalog.json
```

## Test Results

### All Tests
```
173 passed in 1.03s
```

### Coverage
- Catalog Builder: 22 tests
- Architecture Scorer: 151 tests
- 25 context file scenarios covering all treatments and complexity levels

## Blocking Issues
None.

## GitHub Issues Created
1. [#1 - Integrate Catalog Builder into Recommendations App](https://github.com/adamswbrown/azure-architecture-categoriser-/issues/1)
2. [#2 - Containerize the Application](https://github.com/adamswbrown/azure-architecture-categoriser-/issues/2)
3. [#3 - Add CodeQL Security Scanning](https://github.com/adamswbrown/azure-architecture-categoriser-/issues/3)

## Recent Changes (2026-01-29)
1. **Recommendations App v1.2** - 3-step wizard flow with improved UX
2. **Documentation Refactor** - Separated docs for each component
3. **GitHub Issues** - Created roadmap for containerization, catalog integration, CodeQL
4. **Theme Configuration** - Force light mode with Azure branding

## Next Actions
1. Containerize the application (Issue #2)
2. Integrate catalog generation into Recommendations App (Issue #1)
3. Add CodeQL security scanning (Issue #3)
4. Improve diagram asset extraction in catalog builder
