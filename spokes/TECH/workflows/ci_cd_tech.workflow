description: "Pipeline CI/CD sp\xE9cialis\xE9e pour spoke TECH avec tests domaine-sp\xE9\
  cifique"
name: CI/CD Pipeline - Spoke TECH
quality_gates:
- coverage > 85%
- security_audit_passed
- performance_baseline_met
- domain_validation_passed
stages:
- description: "Linting sp\xE9cialis\xE9 tech"
  name: lint
  tools:
  - flake8
  - mypy
  - bandit
  - safety
  - trivy
- coverage_target: 85
  description: Tests tech avec couverture >85%
  framework: pytest + pytest-cov + security-testing
  name: test
- description: "Audit s\xE9curit\xE9 tech"
  name: security
  tools:
  - bandit
  - safety
  - trivy
- description: Tests performance tech
  metrics:
  - response_time < 20ms
  - uptime > 99.9%
  - security_score > 90%
  name: performance
- description: "D\xE9ploiement spoke TECH"
  environment: tech-staging
  name: deploy
