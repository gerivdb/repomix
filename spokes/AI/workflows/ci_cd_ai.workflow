description: "Pipeline CI/CD sp\xE9cialis\xE9 pour spoke AI avec tests domaine-sp\xE9\
  cifique"
name: CI/CD Pipeline - Spoke AI
quality_gates:
- coverage > 85%
- security_audit_passed
- performance_baseline_met
stages:
- description: "Linting sp\xE9cialis\xE9 ai"
  name: lint
  tools:
  - flake8
  - mypy
  - black
  - isort
- coverage_target: 85
  description: Tests ai avec couverture >85%
  framework: pytest + pytest-cov + hypothesis
  name: test
- description: "Audit s\xE9curit\xE9 ai"
  name: security
  tools:
  - bandit
  - safety
  - trivy
- description: "D\xE9ploiement spoke AI"
  environment: ai-staging
  name: deploy
