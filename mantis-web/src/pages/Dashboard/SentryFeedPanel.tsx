import { useAgent } from '../../context/AgentContext';
import { StatusTag } from '../../components/primitives/StatusTag';

export function SentryFeedPanel() {
  const { state } = useAgent();
  const { sentryData } = state;
  const labelColor = sentryData.score < -0.3 ? 'var(--color-error)' : sentryData.score > 0.3 ? 'var(--color-success)' : 'var(--color-warn)';

  return (
    <div>
      <div>SCORE: <span style={{ color: 'var(--color-white)' }}>{sentryData.score.toFixed(2)}</span></div>
      <div>LABEL: <span style={{ color: labelColor }}>[ {sentryData.label} ]</span></div>
      <div>SRCS : <span style={{ color: 'var(--color-white)' }}>{sentryData.sources}</span> data points</div>
      <div style={{ marginTop: '4px' }}>
        {sentryData.signals.map((s, i) => (
          <div key={i} style={{ color: 'var(--color-dim)' }}>&gt; {s}</div>
        ))}
      </div>
    </div>
  );
}
