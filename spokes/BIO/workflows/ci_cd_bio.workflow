description: "Pipeline CI/CD sp\xE9cialis\xE9 pour spoke BIO avec tests domaine-sp\xE9\
  cifique"
name: CI/CD Pipeline - Spoke BIO
quality_gates:
- coverage > 85%
- security_audit_passed
- performance_baseline_met
stages:
- description: "Linting sp\xE9cialis\xE9 bio"
  name: lint
  tools:
  - flake8
  - pylint
  - biopython-lint
- coverage_target: 85
  description: Tests bio avec couverture >85%
  framework: pytest + biopython-test
  name: test
- description: "Audit s\xE9curit\xE9 bio"
  name: security
  tools:
  - bandit
  - safety
  - trivy
- description: "D\xE9ploiement spoke BIO"
  environment: bio-staging
  name: deploy
