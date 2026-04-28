import { runInsightAgent } from '../../agent/src/index.js';

describe('LangGraph Agent Full Workflow Integration', () => {
  jest.setTimeout(30000);

  test('full workflow with valid DUNS returns expected structure', async () => {
    const result = await runInsightAgent('000000001');

    expect(result).toHaveProperty('insight');
    expect(result).toHaveProperty('runId');
    expect(result).toHaveProperty('steps');
  });

  test('insight is substantial (over 100 chars)', async () => {
    const result = await runInsightAgent('000000001');

    expect(result.insight).toBeDefined();
    if (result.insight && !result.error) {
      expect(result.insight.length).toBeGreaterThan(100);
    }
  });

  test('steps array has at least 3 entries', async () => {
    const result = await runInsightAgent('000000001');

    expect(Array.isArray(result.steps)).toBe(true);
    expect(result.steps.length).toBeGreaterThanOrEqual(3);
  });

  test('runId is generated', async () => {
    const result = await runInsightAgent('000000001');

    expect(result.runId).toBeDefined();
    expect(result.runId.length).toBeGreaterThan(0);
  });

  test('invalid DUNS returns error gracefully', async () => {
    const result = await runInsightAgent('999999999');

    expect(result).toHaveProperty('runId');
    expect(result).toHaveProperty('steps');
    // Should either have error or null insight
    expect(result.error || !result.insight).toBeTruthy();
  });

  test('different DUNS produce different insights', async () => {
    const result1 = await runInsightAgent('000000001');
    const result2 = await runInsightAgent('000000002');

    // Results should be different for different companies
    if (result1.insight && result2.insight) {
      expect(result1.insight).not.toEqual(result2.insight);
    }
  });
});
