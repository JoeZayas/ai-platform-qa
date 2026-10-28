import { StateGraph } from '@langchain/langgraph';
import { BaseMessage } from '@langchain/core/messages';
import { ChatAnthropic } from '@langchain/anthropic';
import axios from 'axios';

const llm = new ChatAnthropic({
  model: 'claude-haiku-4-5-20251001',
  temperature: 0.7
});

const agentState = {
  dunsNumber: String,
  companyData: Object,
  creditData: Object,
  webContext: String,
  insight: String,
  error: String,
  steps: [String]
};

const workflow = new StateGraph({ channels: agentState });

// Node: fetchCompanyData
const fetchCompanyData = async (state) => {
  try {
    const response = await axios.get(
      `http://localhost:3000/companies/${state.dunsNumber}`,
      { timeout: 5000 }
    );
    return {
      ...state,
      companyData: response.data,
      steps: [...(state.steps || []), 'Fetched company data']
    };
  } catch (error) {
    return {
      ...state,
      error: `Failed to fetch company data: ${error.message}`,
      steps: [...(state.steps || []), 'Failed to fetch company data']
    };
  }
};

// Node: fetchCreditData
const fetchCreditData = async (state) => {
  if (state.error) {
    return state;
  }

  try {
    const response = await axios.get(
      `http://localhost:3000/companies/${state.dunsNumber}/credit-score`,
      {
        headers: { Authorization: 'Bearer dummy-token' },
        timeout: 5000
      }
    );
    return {
      ...state,
      creditData: response.data,
      steps: [...state.steps, 'Fetched credit data']
    };
  } catch (error) {
    return {
      ...state,
      error: `Failed to fetch credit data: ${error.message}`,
      steps: [...state.steps, 'Failed to fetch credit data']
    };
  }
};

// Node: generateInsight
const generateInsight = async (state) => {
  if (state.error) {
    return state;
  }

  try {
    const systemPrompt = `You are a Dun & Bradstreet business intelligence analyst.
Given the following company profile and credit data, generate a concise 3-sentence
business insight covering: market position, financial health indicators, and one
key risk or opportunity. Be factual, professional, and data-driven.`;

    const userMessage = `
Company: ${state.companyData.name}
Industry: ${state.companyData.industry}
Employees: ${state.companyData.employeeCount}
Revenue: $${state.companyData.annualRevenue}
Founded: ${state.companyData.founded}
Description: ${state.companyData.description}

Credit Score: ${state.creditData?.creditScore || 'Unknown'}
Risk Level: ${state.creditData?.riskLevel || 'Unknown'}
Debt Ratio: ${state.creditData?.debtRatio?.toFixed(2) || 'Unknown'}
Payment History: ${state.creditData?.paymentHistory || 'Unknown'}
`;

    const response = await llm.invoke([
      { role: 'system', content: systemPrompt },
      { role: 'user', content: userMessage }
    ]);

    const insight = response.content;

    return {
      ...state,
      insight,
      steps: [...state.steps, 'Generated business insight']
    };
  } catch (error) {
    return {
      ...state,
      error: `Failed to generate insight: ${error.message}`,
      steps: [...state.steps, 'Failed to generate insight']
    };
  }
};

// Node: handleError
const handleError = async (state) => {
  return {
    ...state,
    insight: null,
    steps: [...state.steps, 'Error handling triggered']
  };
};

// Add nodes
workflow.addNode('fetchCompanyData', fetchCompanyData);
workflow.addNode('fetchCreditData', fetchCreditData);
workflow.addNode('generateInsight', generateInsight);
workflow.addNode('handleError', handleError);

// Add edges
workflow.setEntryPoint('fetchCompanyData');
workflow.addEdge('fetchCompanyData', 'fetchCreditData');
workflow.addEdge('fetchCreditData', 'generateInsight');
workflow.addEdge('generateInsight', '__end__');
workflow.addEdge('handleError', '__end__');

// Conditional routing for error handling
workflow.addConditionalEdges('fetchCompanyData', (state) => {
  return state.error ? 'handleError' : 'fetchCreditData';
});

workflow.addConditionalEdges('fetchCreditData', (state) => {
  return state.error ? 'handleError' : 'generateInsight';
});

const graph = workflow.compile();

export async function runInsightAgent(dunsNumber) {
  try {
    const initialState = {
      dunsNumber,
      companyData: null,
      creditData: null,
      webContext: null,
      insight: null,
      error: null,
      steps: []
    };

    const result = await graph.invoke(initialState, { runName: `insight-${dunsNumber}` });

    return {
      insight: result.insight || result.error || 'Unable to generate insight',
      runId: `run-${Date.now()}`,
      steps: result.steps
    };
  } catch (error) {
    console.error('Agent error:', error);
    return {
      insight: null,
      runId: `run-${Date.now()}`,
      steps: ['Error during agent execution'],
      error: error.message
    };
  }
}

export { graph };
