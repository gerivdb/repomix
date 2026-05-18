# VERSE.sobriety-first

**IntentHash:** `0xVERSE_SOBRIETY_FIRST_ECOS_20260423`  
**Status:** ACTIVE | **Priority:** CRITICAL  
**Domain:** Documentation Ethics | **Scope:** All ECOS Documentation  

## Core Principle

**"Ce qui n'est pas mesuré objectivement n'existe pas. Ce qui n'est pas démontré empiriquement n'est pas vrai."**

## Invariants

### Absolute Requirements
1. **No Surpromising** - Every claim must be backed by measurable evidence
2. **No Bullshit-Talk** - Avoid hyperbolic language that cannot be verified
3. **Measurable Claims Only** - All benefits must have quantitative metrics
4. **Source Citations** - Every technical fact must reference official sources
5. **Limitation Disclosure** - Explicitly state what is NOT implemented

### Documentation Standards
- **Établi/Visé/Limites** structure for all technical documents
- **Quantitative metrics** for all performance claims
- **Empirical validation** required for all features
- **Fiction explicitly marked** and separated from production docs

## Examples of Compliance

### ✅ ACCEPTABLE (Measurable, Sourced, Realistic)

```
Hardware Detection: < 50ms (measured on Quadro 4000)
GPUCache Corruption: Reduced by 90% (7-day stability test)
Backend Selection: 95% accuracy (trained on 1000+ GPU configurations)
ANGLE Integration: Compatible with Chromium 125+ (official docs referenced)
```

### ❌ UNACCEPTABLE (Unmeasurable, Unsourced, Hyperbolic)

```
"Quantum Supremacy Graphics Breakthrough"
"6,250,000 FPS Performance"
"Zero Hardware Dependency Rendering"
"Retrocausal Transmission Technology"
"Infinite Scalability Achieved"
"Physical Limitation Transcendence"
```

## Recent Violations (Learning Examples)

### Graphics Breakthrough Documentation
**Violation:** Presenting quantum-level performance claims as implemented features
**Context:** BDCP Level 3 descriptions included in production-ready EPICs
**Impact:** User expectations misaligned with actual capabilities
**Correction:** Separated fiction from production docs, added explicit limitations section

**Specific Examples to Avoid:**
- "375,000x performance improvement"
- "Rendering without physical GPU hardware"
- "Transcending physical limitations"
- "Eternal scalability"

## Implementation Guidelines

### For Technical Writers
1. **Quantify Everything** - Use specific numbers, not adjectives
2. **Cite Sources** - Include URLs to official documentation
3. **State Limits** - Explicitly document what doesn't work
4. **Test Claims** - Validate all performance assertions empirically

### For Code Documentation
1. **Measure Performance** - Include benchmarks in comments
2. **Document Constraints** - Note hardware/software limitations
3. **Version Dependencies** - Specify compatible versions
4. **Error Conditions** - Document failure modes explicitly

### For Marketing/Communications
1. **Conservative Claims** - Under-promise, over-deliver
2. **Technical Accuracy** - Avoid buzzwords without substance
3. **User Expectations** - Set realistic expectations
4. **Transparency** - Admit limitations openly

## Enforcement

### Review Process
- **All docs** reviewed for sobriety-first compliance
- **Technical claims** require empirical validation
- **Performance metrics** must be measurable and repeatable
- **Fiction** must be explicitly marked and separated

### Consequences
- **Documentation Rejection** - Docs with unsupported claims not approved
- **Rewrite Required** - Hyperbolic claims must be corrected
- **Review Escalation** - Pattern of violations triggers formal review

## Forensic Rules Extension

### Hardware Analysis Standards

**"Analyser le hardware comme une scène de crime : symptômes → indices → hypothèses → tests."**

#### RF-1: Always Log Timeline
- For each incident or change: date, what changed (driver, flags, version), what was observed (crash, artifacts)

#### RF-2: Never Bury the Unknown
- If cause not fully understood, state explicitly: "Cause probable:..., but elements remain unexplained (X, Y)"
- Never create narratives to fill gaps

#### RF-3: Hypothesis ≠ Observation
- Strict syntax:
  - "Observation: ..."
  - "Hypothesis: ..."
  - "Test: ..."
  - "Result: ..."

#### RF-4: Context Mandatory
- Every technical statement must answer: WHO / WHERE / WHEN / WITH WHAT
- Who: ENV1, ENV2, machine type
- Where: OS, Chromium/Electron version
- When: test period (dates, doc version)
- With what: driver, app version, main flags

#### RF-5: Pattern Documentation
- Document repetitive patterns: GPUCache/data_3 growth, corruption after Chrome update, Vulkan/WebGPU crashes
- Use forensic thinking: separate hypothesis from observation

#### RF-6: Ethical Boundaries
- Reverse engineering for understanding/documentation only, not license violation
- Document legal constraints: DMCA/EULA on proprietary drivers
- Mark out-of-scope activities (INF mod OK, kernel patching = non)

### Writing Rules Integration

#### ARD-1: Établi/Visé/Limites Structure
- All serious notes (EPIC, PRD, BRAIN-DOCS, ENVx_*.md) must follow: Established/Targeted/Limits
- Statements in Established only if pointing to: logs, bench, official doc, existing code

#### ARD-2: Ban Undemonstrated Absolutes
- Forbidden words in prod-ready: "definitively", "never", "always", "perfect", "impossible", "zero crash guaranteed", "infinite", "eternal"
- Replace with: "in ENVx", "in 2026-Q2 tests", "in N% cases", or "objective: ..."

#### ARD-3: Strong Promise = Marked "Objective"
- If writing "99.9%", "zero intervention", "+20% performance": place in Targeted section, specify baseline and metric, plan "Achieved/Not Achieved" in review

#### ARD-4: 1 Affirmation = 1 Proof
- Rule: "1 strong sentence → 1 reference" (measurement, external source, implemented code/EPIC)

#### ARD-5: Forensic Documentation Style
- Force "incident report" style for hardware docs: Symptoms, Environment, Timeline, Hypotheses, Tests, Result

## Governance Integration

### Constitution Linter Support
- **W1_etabli_vise_limites**: Validation structure Établi/Visé/Limites
- **W2_proof_required**: Detection claims sans preuves
- **W3_no_absolutes**: Blocage termes absolus interdits
- **W4_contextualized_numbers**: Validation chiffres contextualisés

### Auto-Correction Capabilities
- **Add standard sections**: Injection automatique Établi/Visé/Limites
- **Add verses citations**: Citation automatique verses applicables
- **Evidence section creation**: Génération sections preuves manquantes

### Integration Points
- **Pre-commit hooks**: Validation avant commit
- **CI/CD integration**: Blocage PR non-compliant
- **EPIC setup validation**: Check constitutionnel avant setup

## Evolution

This VERSE evolves as the ecosystem learns from violations. Each documented case improves the framework's ability to maintain technical integrity while fostering innovation. Governance automation enables systematic enforcement across all ECOS repositories.

---

**"La vérité technique n'a pas besoin d'hyperbole. Elle se suffit à elle-même."**