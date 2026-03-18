export function ProgressBar({ value }: { value: number }) {
  const TOTAL = 16;
  const filled = Math.round(value * TOTAL);
  const empty = TOTAL - filled;
  return (
    <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-primary)' }}>
      <span style={{ color: 'var(--color-dim)' }}>{'['}</span>
      <span style={{ color: 'var(--color-success)' }}>{'█'.repeat(filled)}</span>
      <span style={{ color: 'var(--color-dim)' }}>{'░'.repeat(empty)}</span>
      <span style={{ color: 'var(--color-dim)' }}>{'] '}</span>
      <span style={{ color: 'var(--color-white)' }}>{Math.round(value * 100)}%</span>
    </span>
  );
}
