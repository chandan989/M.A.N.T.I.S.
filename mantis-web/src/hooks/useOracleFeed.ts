import { useEffect } from 'react';
import { useAgent } from '../context/AgentContext';
import { generateOracleSnapshot } from '../data/mockData';

export function useOracleFeed() {
  const { dispatch } = useAgent();

  useEffect(() => {
    const timer = setInterval(() => {
      dispatch({ type: 'UPDATE_ORACLE', payload: generateOracleSnapshot() });
    }, 15000);
    return () => clearInterval(timer);
  }, [dispatch]);
}
