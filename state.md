# Azure Architecture Catalog Builder - Project State

## Current Phase
**Phase 2: GUI & Scoring Enhancements - COMPLETE**

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

## Architecture Decisions

### Technology Stack
- Python 3.11+
- Click for CLI
- Pydantic for schema validation
- PyYAML for frontmatter parsing
- Rich for terminal output
- GitPython for git metadata
- Streamlit for GUI (optional dependency)

### Project Structure
```
azure-architecture-categoriser-/
├── src/
│   ├── catalog_builder/          # Catalog generation
│   │   ├── cli.py, parser.py, detector.py
│   │   ├── extractor.py, classifier.py
│   │   ├── schema.py, catalog.py, config.py
│   ├── architecture_scorer/      # Architecture scoring
│   │   ├── cli.py, scorer.py, schema.py
│   │   ├── normalizer.py, intent_deriver.py
│   │   ├── question_generator.py, matcher.py
│   └── catalog_builder_gui/      # Streamlit GUI
│       ├── app.py, state/
│       └── components/
├── tests/
│   ├── test_catalog_builder.py
│   ├── test_architecture_scorer.py
│   └── context_files/            # 25 test scenarios
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

## Recent Changes (2026-01-29)
1. **Streamlit GUI** - Visual config editor with repo clone/pull
2. **Network Exposure Question** - Always asked, affects Public/Private Link selection
3. **Learn URL Fix** - Proper Microsoft Learn URLs (strip `-content` suffix)

## Next Actions
1. Add manual classification overrides system
2. Enhance Azure service normalization
3. Add incremental catalog updates
4. Connect network exposure to architecture matching logic
