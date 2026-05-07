import { expect, test, describe } from '@jest/globals';
import * as fs from 'fs';
import * as path from 'path';

describe('EPICs Integration Tests - TDD', () => {
  const epicsDir = path.join(__dirname, '../../epics');

  test('All 11 EPICs should exist', () => {
    const expectedEpics = [
      'EPIC-OUROBOROS-WAVE-INTEGRATION.md',
      'EPIC-WAVE-ONTOLOGY-NEXUS-INTEGRATION.md',
      'EPIC-OUROBOROS-RLM-BRIDGE.md',
      'EPIC-NEXUS-16-AXES-RLM-EVALUATION.md',
      'EPIC-OPS-RLM-CONVERGENCE-MODEL.md',
      'EPIC-DYNAMIC-SKILLS-RLM-ENRICHMENT.md',
      'EPIC-SKILLS-RLM-OUROBOROS-VIRTUOUS-CYCLE.md',
      'EPIC-RLM-CONVERGENCE-METRICS-WAL.md',
      'EPIC-BRAIN-GATEWAY-RLM-PROVIDER.md',
      'EPIC-NEXUS-FRACTAL-OUROBOROS-RLM-ARCHITECTURE.md',
      'EPIC-COMPLETE-NEXUS-OUROBOROS-RLM-SYMBIOSIS.md'
    ];

    expectedEpics.forEach(epic => {
      const epicPath = path.join(epicsDir, epic);
      expect(fs.existsSync(epicPath)).toBe(true);
    });
  });

  test('Each EPIC should have proper structure', () => {
    const ouroborosRlmEpics = [
      'EPIC-OUROBOROS-WAVE-INTEGRATION.md',
      'EPIC-WAVE-ONTOLOGY-NEXUS-INTEGRATION.md',
      'EPIC-OUROBOROS-RLM-BRIDGE.md',
      'EPIC-NEXUS-16-AXES-RLM-EVALUATION.md',
      'EPIC-OPS-RLM-CONVERGENCE-MODEL.md',
      'EPIC-DYNAMIC-SKILLS-RLM-ENRICHMENT.md',
      'EPIC-SKILLS-RLM-OUROBOROS-VIRTUOUS-CYCLE.md',
      'EPIC-RLM-CONVERGENCE-METRICS-WAL.md',
      'EPIC-BRAIN-GATEWAY-RLM-PROVIDER.md',
      'EPIC-NEXUS-FRACTAL-OUROBOROS-RLM-ARCHITECTURE.md',
      'EPIC-COMPLETE-NEXUS-OUROBOROS-RLM-SYMBIOSIS.md'
    ];

    ouroborosRlmEpics.forEach(epicFile => {
      const content = fs.readFileSync(path.join(epicsDir, epicFile), 'utf8');

      // Should have title
      expect(content).toMatch(/^# EPIC-/m);

      // Should have description/objective section
      expect(content).toMatch(/## (Description|Objectifs)/m);

      // Should be marked as implemented
      expect(content).toMatch(/## Statut\s*✅ Implémenté/m);
    });
  });

  test('EPIC content should reference key metrics', () => {
    const metrics = [
      '128 742', // gain factor
      '0.001', // semantic loss
      'HITL = 0' // human in the loop
    ];

    const convergenceModelEpic = path.join(epicsDir, 'EPIC-OPS-RLM-CONVERGENCE-MODEL.md');
    const content = fs.readFileSync(convergenceModelEpic, 'utf8');

    metrics.forEach(metric => {
      expect(content).toContain(metric);
    });
  });
});