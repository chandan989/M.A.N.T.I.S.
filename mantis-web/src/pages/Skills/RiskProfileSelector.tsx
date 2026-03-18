import { useAgent } from '../../context/AgentContext';

const PROFILES = [
  { key: 'conservative' as const, label: 'CONSERVATIVE', details: 'Max Vol: 0.35  |  Min Harvest: 3h  |  Withdraw @ Vol > 0.80' },
  { key: 'moderate' as const, label: 'MODERATE', details: 'Max Vol: 0.60  |  Min Harvest: 2h  |  Withdraw @ Vol > 0.90' },
  { key: 'aggressive' as const, label: 'AGGRESSIVE', details: 'Max Vol: 0.90  |  Min Harvest: 1h  |  Withdraw @ Vol > 1.00' },
];

export function RiskProfileSelector() {
  const { state, dispatch } = useAgent();

  return (
    <div className="risk-profile">
      <div style={{ color: 'var(--color-dim)', textTransform: 'uppercase', marginBottom: '4px' }}>RISK PROFILE:</div>
      {PROFILES.map(p => (
        <div
          key={p.key}
          className={`risk-option ${state.riskProfile === p.key ? 'risk-option--active' : ''}`}
          onClick={() => dispatch({ type: 'SET_RISK_PROFILE', payload: p.key })}
        >
          <span>{state.riskProfile === p.key ? '(x)' : '( )'}</span>
          <span>{p.label}</span>
          <span className="risk-details">[ {p.details} ]</span>
        </div>
      ))}
    </div>
  );
}
