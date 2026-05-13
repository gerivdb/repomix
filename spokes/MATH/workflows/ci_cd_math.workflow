description: "Pipeline CI/CD sp\xE9cialis\xE9 pour spoke MATH avec tests domaine-sp\xE9\
  cifique"
name: CI/CD Pipeline - Spoke MATH
quality_gates:
- coverage > 85%
- security_audit_passed
- performance_baseline_met
stages:
- description: "Linting sp\xE9cialis\xE9 math"
  name: lint
  tools:
  - flake8
  - mypy
  - doctest
  - sympy-lint
- coverage_target: 85
  description: Tests math avec couverture >85%
  framework: pytest + sympy + numpy.testing
  name: test
- description: "Audit s\xE9curit\xE9 math"
  name: security
  tools:
  - bandit
  - safety
  - trivy
- description: "D\xE9ploiement spoke MATH"
  environment: math-staging
  name: deploy
