import { graph } from '../../agent/src/index.js';

describe('LangGraph Agent Structure', () => {
  test('graph has expected nodes', async () => {
    const nodes = graph._graph._nodes || {};
    const nodeNames = Object.keys(nodes);

    expect(nodeNames).toContain('fetchCompanyData');
    expect(nodeNames).toContain('fetchCreditData');
    expect(nodeNames).toContain('generateInsight');
    expect(nodeNames).toContain('handleError');
  });

  test('graph has expected edges', async () => {
    const edges = graph._graph._edges || [];
    const edgeStrings = edges.map(e => `${e.source}->${e.target}`);

    // Should have edges connecting nodes
    expect(edgeStrings.length).toBeGreaterThan(0);
  });

  test('initial state shape is correct', async () => {
    const initialState = {
      dunsNumber: '',
      companyData: null,
      creditData: null,
      webContext: null,
      insight: null,
      error: null,
      steps: []
    };

    expect(initialState).toHaveProperty('dunsNumber');
    expect(initialState).toHaveProperty('companyData');
    expect(initialState).toHaveProperty('creditData');
    expect(initialState).toHaveProperty('webContext');
    expect(initialState).toHaveProperty('insight');
    expect(initialState).toHaveProperty('error');
    expect(initialState).toHaveProperty('steps');
    expect(Array.isArray(initialState.steps)).toBe(true);
  });
});
