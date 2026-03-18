import { useState } from 'react';
import { useAgent } from '../../context/AgentContext';
import { useOracleFeed } from '../../hooks/useOracleFeed';
import { PanelBox } from '../../components/primitives/PanelBox';
import { StatusTag } from '../../components/primitives/StatusTag';
import { ConfirmModal } from '../../components/ConfirmModal/ConfirmModal';
import { ExecutionLog } from './ExecutionLog';
import { OracleFeedPanel } from './OracleFeedPanel';
import { VaultStatusPanel } from './VaultStatusPanel';
import { SentryFeedPanel } from './SentryFeedPanel';
import './Dashboard.css';

export default function Dashboard() {
  const { state } = useAgent();
  const [modal, setModal] = useState<{ title: string; action: string; variant: 'danger' | 'info' } | null>(null);
  useOracleFeed();

  return (
    <div className="dashboard-layout">
      <div className="dashboard-left">
        <PanelBox title="SYSTEM STATUS" doubleLine>
          <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <span>SYS.MODE: <StatusTag status={state.agentRunning ? 'ACTIVE' : 'IDLE'} /></span>
            <span>NET: <span style={{ color: 'var(--color-success)' }}>[MAINNET]</span></span>
            <span>AGENT: <StatusTag status={state.agentRunning ? 'ACTIVE' : 'IDLE'} /></span>
          </div>
          <div style={{ marginTop: '4px' }}>
            WALLET: <span style={{ color: 'var(--color-success)' }}>{state.walletId}</span>
            {' '}<span style={{ color: 'var(--color-white)' }}>{state.hbarBalance.toLocaleString()} HBAR</span>
          </div>
        </PanelBox>

        <PanelBox title="EXECUTION LOG">
          <ExecutionLog />
        </PanelBox>
      </div>

      <div className="dashboard-right">
        <PanelBox title="ORACLE FEED">
          <OracleFeedPanel />
        </PanelBox>

        <PanelBox title="VAULT STATUS">
          <VaultStatusPanel />
        </PanelBox>

        <PanelBox title="SENTRY FEED">
          <SentryFeedPanel />
        </PanelBox>

        <PanelBox title="QUICK ACTIONS">
          <div className="quick-actions">
            <button className="btn" disabled={state.actionInFlight} onClick={() => setModal({ title: 'HARVEST', action: 'HARVEST', variant: 'info' })}>
              [ HARVEST ]
            </button>
            <button className="btn" disabled={state.actionInFlight} onClick={() => setModal({ title: 'HARVEST+SWAP', action: 'HARVEST_SWAP', variant: 'info' })}>
              [ HARVEST+SWAP ]
            </button>
            <button className="btn btn--danger" disabled={state.actionInFlight} onClick={() => setModal({ title: 'EMERGENCY WITHDRAW', action: 'EMERGENCY_WITHDRAW', variant: 'danger' })}>
              [ EMERGENCY WITHDRAW ]
            </button>
          </div>
        </PanelBox>
      </div>

      {modal && (
        <ConfirmModal
          title={`CONFIRM: ${modal.title}`}
          message={`Execute ${modal.action} on active vault?`}
          targetLabel={state.activeVaultId}
          variant={modal.variant}
          onCancel={() => setModal(null)}
          onConfirm={() => setModal(null)}
        />
      )}
    </div>
  );
}
