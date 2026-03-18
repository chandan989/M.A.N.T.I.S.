export function Toggle({ value, onChange, label }: { value: boolean; onChange: (v: boolean) => void; label: string }) {
  return (
    <span style={{ fontFamily: 'var(--font-mono)' }}>
      <span style={{ color: 'var(--color-dim)', textTransform: 'uppercase', marginRight: '8px' }}>{label}</span>
      <span
        onClick={() => onChange(!value)}
        style={{ cursor: 'pointer', color: value ? 'var(--color-success)' : 'var(--color-dim)' }}
      >
        {value ? '[███|   ]' : '[   |███]'}
      </span>
      <span style={{ color: value ? 'var(--color-success)' : 'var(--color-dim)', marginLeft: '6px' }}>
        {value ? 'ON' : 'OFF'}
      </span>
    </span>
  );
}
