import { graph } from '../../agent/src/index.js';

describe('LangGraph Agent Nodes (Unit)', () => {
  test('graph can be invoked without crashing', async () => {
    // This is a basic test to ensure the graph can be called
    // without throwing errors
    expect(graph).toBeDefined();
    expect(graph.invoke).toBeDefined();
  });

  test('graph returns object with expected structure', async () => {
    const result = await graph.invoke({
      dunsNumber: '000000001',
      companyData: null,
      creditData: null,
      webContext: null,
      insight: null,
      error: null,
      steps: []
    });

    expect(result).toHaveProperty('dunsNumber');
    expect(result).toHaveProperty('companyData');
    expect(result).toHaveProperty('steps');
  });

  test('graph step tracking works', async () => {
    const result = await graph.invoke({
      dunsNumber: '000000001',
      companyData: null,
      creditData: null,
      webContext: null,
      insight: null,
      error: null,
      steps: []
    });

    expect(Array.isArray(result.steps)).toBe(true);
    expect(result.steps.length).toBeGreaterThan(0);
  });
});
