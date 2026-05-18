# EPIC-02 Spokes - Configuration

## Spokes à Créer

1. **VERSES-PHYSICS** - wolfram_physics_2020.verse.yaml
2. **VERSES-MATH** - mathematical_framework.verse.yaml
3. **VERSES-SCIENCE** - fermi_ever_breakbreakthroughs.verse.yaml
4. **VERSES-AI** - ai_reasoning_patterns.verse.yaml
5. **VERSES-BIO** - biological_systems.verse.yaml
6. **VERSES-TECH** - technology_stack.verse.yaml

## Templates CI/CD

```yaml
name: VERSE Validation
on: [push, pull_request]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Validate schema
        run: python -m verses.validate
      - name: Run tests
        run: pytest
```