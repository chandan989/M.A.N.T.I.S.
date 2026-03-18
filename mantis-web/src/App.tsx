import { useEffect } from 'react';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import { AgentProvider, useAgent } from './context/AgentContext';
import { AppShell } from './components/AppShell/AppShell';
import { generateLogEntry } from './data/mockData';
import Landing from './pages/Landing/Landing';
import Dashboard from './pages/Dashboard/Dashboard';
import VaultOps from './pages/VaultOps/VaultOps';
import Skills from './pages/Skills/Skills';
import System from './pages/System/System';

function LogTicker() {
  const { dispatch, state } = useAgent();

  useEffect(() => {
    if (!state.agentRunning) return;
    const interval = 8000 + Math.random() * 4000;
    const timer = setTimeout(() => {
      const entry = generateLogEntry();
      dispatch({ type: 'ADD_LOG', payload: entry });
      if (entry.action) {
        dispatch({ type: 'UPDATE_LAST_ACTION', payload: { action: entry.action, ts: Date.now() } });
      }
    }, interval);
    return () => clearTimeout(timer);
  }, [state.executionLog, state.agentRunning, dispatch]);

  return null;
}

function AppInner() {
  return (
    <>
      <LogTicker />
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/dashboard" element={<AppShell><Dashboard /></AppShell>} />
        <Route path="/vault" element={<AppShell><VaultOps /></AppShell>} />
        <Route path="/skills" element={<AppShell><Skills /></AppShell>} />
        <Route path="/system" element={<AppShell><System /></AppShell>} />
      </Routes>
    </>
  );
}

const App = () => (
  <AgentProvider>
    <BrowserRouter>
      <AppInner />
    </BrowserRouter>
  </AgentProvider>
);

export default App;
