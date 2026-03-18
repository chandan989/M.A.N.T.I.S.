import { PanelBox } from '../../components/primitives/PanelBox';
import { StatusTag } from '../../components/primitives/StatusTag';
import { Toggle } from '../../components/primitives/Toggle';
import { useState } from 'react';

interface SkillPanelProps {
  name: string;
  version: string;
  sources: string;
  lastRun: string;
  nextRun: string;
  details: React.ReactNode;
  initialActive?: boolean;
}

export function SkillPanel({ name, version, sources, lastRun, nextRun, details, initialActive = true }: SkillPanelProps) {
  const [active, setActive] = useState(initialActive);

  return (
    <PanelBox title={`${name} SKILL`}>
      <div>
        <span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>STATUS  : </span>
        <StatusTag status={active ? 'ACTIVE' : 'IDLE'} />
        <span style={{ marginLeft: '16px', color: 'var(--color-dim)', textTransform: 'uppercase' }}>VERSION : </span>
        <span style={{ color: 'var(--color-white)' }}>{version}</span>
      </div>
      <div>
        <span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>SOURCES : </span>
        {sources}
      </div>
      <div>
        <span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>LAST RUN: </span>
        <span style={{ color: 'var(--color-white)' }}>{lastRun}</span>
        <span style={{ marginLeft: '16px', color: 'var(--color-dim)', textTransform: 'uppercase' }}>NEXT RUN: </span>
        <span style={{ color: 'var(--color-white)' }}>{nextRun}</span>
      </div>
      {details}
      <div style={{ marginTop: '8px', borderTop: '1px solid var(--color-dim)', paddingTop: '6px' }}>
        <Toggle value={active} onChange={setActive} label="TOGGLE  :" />
      </div>
    </PanelBox>
  );
}
