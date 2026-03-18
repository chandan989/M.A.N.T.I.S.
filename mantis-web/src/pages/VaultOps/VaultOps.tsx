import { useState } from 'react';
import { useAgent } from '../../context/AgentContext';
import { PanelBox } from '../../components/primitives/PanelBox';
import { ConfirmModal } from '../../components/ConfirmModal/ConfirmModal';
import { VaultDetailPanel } from './VaultDetailPanel';
import { APYChart } from './APYChart';
import { TxHistoryTable } from './TxHistoryTable';
import './VaultOps.css';

export default function VaultOps() {
  const { state, dispatch } = useAgent();
  const [showModal, setShowModal] = useState(false);
  const [lowerBound, setLowerBound] = useState('');
  const [upperBound, setUpperBound] = useState('');

  return (
    <div className="vault-ops-layout">
      <PanelBox title="VAULT SELECTOR">
        <span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>TARGET VAULT: </span>
        <select
          className="terminal-select"
          value={state.activeVaultId}
          onChange={e => dispatch({ type: 'SET_ACTIVE_VAULT', payload: e.target.value })}
        >
          {state.vaultData.map(v => (
            <option key={v.id} value={v.id}>{v.name} ▼</option>
          ))}
        </select>
      </PanelBox>

      <VaultDetailPanel />
      <APYChart />

      <PanelBox title="RANGE ADJUSTMENT">
        <div className="range-form">
          <div>
            <label>NEW LOWER BOUND:</label>
            <span style={{ color: 'var(--color-dim)' }}>&gt; </span>
            <input
              className="terminal-input"
              type="text"
              placeholder="$0.000"
              value={lowerBound}
              onChange={e => setLowerBound(e.target.value)}
            />
          </div>
          <div>
            <label>NEW UPPER BOUND:</label>
            <span style={{ color: 'var(--color-dim)' }}>&gt; </span>
            <input
              className="terminal-input"
              type="text"
              placeholder="$0.000"
              value={upperBound}
              onChange={e => setUpperBound(e.target.value)}
            />
          </div>
          <button className="btn" onClick={() => setShowModal(true)} disabled={state.actionInFlight}>
            [ SUBMIT REBALANCE ]
          </button>
        </div>
      </PanelBox>

      <TxHistoryTable />

      {showModal && (
        <ConfirmModal
          title="CONFIRM REBALANCE"
          message={`Rebalance vault to range: ${lowerBound || '?'} – ${upperBound || '?'}`}
          targetLabel={state.activeVaultId}
          onCancel={() => setShowModal(false)}
          onConfirm={() => setShowModal(false)}
        />
      )}
    </div>
  );
}
