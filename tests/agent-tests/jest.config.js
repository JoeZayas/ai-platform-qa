export default {
  testEnvironment: 'node',
  transform: {},
  extensionsToTreatAsEsm: ['.js'],
  testMatch: ['**/*.test.js'],
  collectCoverageFrom: ['agent/src/**/*.js'],
  testTimeout: 30000
};
