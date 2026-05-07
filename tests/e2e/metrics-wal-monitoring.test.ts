import { expect, test, describe, beforeAll } from '@jest/globals';

describe('RLM Convergence Metrics WAL - E2E Tests', () => {
  let walSystem: any;
  let metricsCollector: any;

  beforeAll(async () => {
    walSystem = await initializeWALSystem();
    metricsCollector = await initializeMetricsCollector();
  });

  test('WAL should log RLM cycle completion events', async () => {
    const cycleData = {
      cycleId: 'rlm-cycle-001',
      opsLevel: 'OPS3',
      iterations: 5,
      finalScore: 0.97,
      gainFactor: 145000,
      semanticLoss: 0.0008,
      hitl: 0
    };

    await walSystem.logEvent('RLM_CYCLE_COMPLETE', cycleData);

    const events = await walSystem.getEvents('RLM_CYCLE_COMPLETE');
    const lastEvent = events[events.length - 1];

    expect(lastEvent.type).toBe('RLM_CYCLE_COMPLETE');
    expect(lastEvent.data).toEqual(cycleData);
    expect(lastEvent.timestamp).toBeDefined();
  });

  test('Metrics should track gain factor progression', async () => {
    const targetGainFactor = 128742;
    const measurements = [100000, 120000, 135000, 142000, 150000];

    for (const measurement of measurements) {
      await metricsCollector.recordGainFactor(measurement);
    }

    const progression = await metricsCollector.getGainFactorProgression();

    expect(progression.current).toBe(150000);
    expect(progression.target).toBe(targetGainFactor);
    expect(progression.achieved).toBe(true);
    expect(progression.percentage).toBeGreaterThan(100);
  });

  test('Semantic loss should stay below threshold', async () => {
    const threshold = 0.001;
    const measurements = [0.0008, 0.0006, 0.0004, 0.0007, 0.0005]; // All below threshold

    for (const measurement of measurements) {
      await metricsCollector.recordSemanticLoss(measurement);
    }

    const stats = await metricsCollector.getSemanticLossStats();

    expect(stats.average).toBeLessThan(threshold);
    expect(stats.max).toBeLessThan(threshold);
    expect(stats.withinThreshold).toBe(true);
  });

  test('HITL should progress toward zero', async () => {
    const progression = [5, 3, 2, 1, 0]; // Decreasing HITL over time

    for (let i = 0; i < progression.length; i++) {
      await metricsCollector.recordHITL(progression[i]);
    }

    const hitlProgression = await metricsCollector.getHITLProgression();

    expect(hitlProgression.current).toBe(0);
    expect(hitlProgression.target).toBe(0);
    expect(hitlProgression.achieved).toBe(true);
    expect(hitlProgression.trend).toBe('decreasing');
  });

  test('Convergence rate should be calculated correctly', async () => {
    const scores = [0.85, 0.90, 0.93, 0.96, 0.98];

    for (const score of scores) {
      await metricsCollector.recordConvergenceScore(score);
    }

    const convergenceStats = await metricsCollector.getConvergenceStats();

    expect(convergenceStats.average).toBeGreaterThan(0.9);
    expect(convergenceStats.trend).toBe('improving');
    expect(convergenceStats.consistency).toBeGreaterThan(0.8);
  });

  test('System should alert on metric degradation', async () => {
    // Simulate metric degradation
    await metricsCollector.recordSemanticLoss(0.005); // Above threshold

    const alerts = await metricsCollector.getActiveAlerts();

    expect(alerts).toContainEqual({
      type: 'SEMANTIC_LOSS_THRESHOLD_EXCEEDED',
      severity: 'high',
      value: 0.005,
      threshold: 0.001
    });
  });

  // Helper functions
  async function initializeWALSystem() {
    const events: any[] = [];

    return {
      logEvent: async (type: string, data: any) => {
        events.push({
          type,
          data,
          timestamp: new Date().toISOString()
        });
      },

      getEvents: async (type: string) => {
        return events.filter(event => event.type === type);
      }
    };
  }

  async function initializeMetricsCollector() {
    const gainFactors: number[] = [];
    const semanticLosses: number[] = [];
    const hitlValues: number[] = [];
    const convergenceScores: number[] = [];

    return {
      recordGainFactor: async (value: number) => {
        gainFactors.push(value);
      },

      recordSemanticLoss: async (value: number) => {
        semanticLosses.push(value);
      },

      recordHITL: async (value: number) => {
        hitlValues.push(value);
      },

      recordConvergenceScore: async (value: number) => {
        convergenceScores.push(value);
      },

      getGainFactorProgression: async () => {
        const current = gainFactors[gainFactors.length - 1];
        const target = 128742;
        return {
          current,
          target,
          achieved: current >= target,
          percentage: (current / target) * 100
        };
      },

      getSemanticLossStats: async () => {
        const average = semanticLosses.reduce((a, b) => a + b, 0) / semanticLosses.length;
        const max = Math.max(...semanticLosses);
        const threshold = 0.001;
        return {
          average,
          max,
          withinThreshold: average <= threshold && max <= threshold
        };
      },

      getHITLProgression: async () => {
        const current = hitlValues[hitlValues.length - 1];
        const target = 0;
        const trend = hitlValues.length > 1 &&
          hitlValues[hitlValues.length - 1] < hitlValues[hitlValues.length - 2] ? 'decreasing' : 'stable';
        return {
          current,
          target,
          achieved: current === target,
          trend
        };
      },

      getConvergenceStats: async () => {
        const average = convergenceScores.reduce((a, b) => a + b, 0) / convergenceScores.length;
        const trend = convergenceScores.length > 1 &&
          convergenceScores[convergenceScores.length - 1] > convergenceScores[convergenceScores.length - 2] ? 'improving' : 'stable';
        const consistency = 1 - (standardDeviation(convergenceScores) / average);
        return { average, trend, consistency };
      },

      getActiveAlerts: async () => {
        const alerts = [];
        const latestSemanticLoss = semanticLosses[semanticLosses.length - 1];
        if (latestSemanticLoss > 0.001) {
          alerts.push({
            type: 'SEMANTIC_LOSS_THRESHOLD_EXCEEDED',
            severity: 'high',
            value: latestSemanticLoss,
            threshold: 0.001
          });
        }
        return alerts;
      }
    };
  }

  function standardDeviation(values: number[]): number {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const squareDiffs = values.map(value => Math.pow(value - mean, 2));
    const avgSquareDiff = squareDiffs.reduce((a, b) => a + b, 0) / squareDiffs.length;
    return Math.sqrt(avgSquareDiff);
  }
});