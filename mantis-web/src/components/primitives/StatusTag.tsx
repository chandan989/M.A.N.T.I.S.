import React from 'react';

type TagStatus = 'OK' | 'WARN' | 'FAIL' | 'IDLE' | 'ACTIVE' | 'ERR';

const TAG_MAP: Record<TagStatus, { label: string; color: string }> = {
  OK:     { label: '  OK  ', color: 'var(--color-success)' },
  ACTIVE: { label: 'ACTIVE', color: 'var(--color-success)' },
  WARN:   { label: ' WARN ', color: 'var(--color-warn)' },
  FAIL:   { label: ' FAIL ', color: 'var(--color-error)' },
  ERR:    { label: '  ERR ', color: 'var(--color-error)' },
  IDLE:   { label: ' IDLE ', color: 'var(--color-dim)' },
};

export function StatusTag({ status }: { status: TagStatus }) {
  const tag = TAG_MAP[status];
  return (
    <span style={{ color: tag.color, fontFamily: 'var(--font-mono)' }}>
      [{tag.label}]
    </span>
  );
}
