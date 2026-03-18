import { useState } from 'react';
import { useAgent } from '../../context/AgentContext';
import { PanelBox } from '../../components/primitives/PanelBox';
import { Toggle } from '../../components/primitives/Toggle';
import { ProgressBar } from '../../components/primitives/ProgressBar';
import { StatusTag } from '../../components/primitives/StatusTag';
import { ConfirmModal } from '../../components/ConfirmModal/ConfirmModal';
import { generateLogEntry } from '../../data/mockData';
import './System.css';

export default function System() {
  const { state, dispatch } = useAgent();
  const [modal, setModal] = useState<string | null>(null);
  const [alertCondition, setAlertCondition] = useState<'above' | 'below'>('below');
  const [alertThreshold, setAlertThreshold] = useState('');

  const handleExportLog = () => {
    const text = state.executionLog
      .map(e => `${e.timestamp} > ${e.phase.padEnd(5)}: ${e.message}${e.action ? ' ' + e.action : ''}${e.status ? ' [' + e.status + ']' : ''}`)
      .join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'mantis-execution-log.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  const handleForceTick = () => {
    const entry = generateLogEntry();
    dispatch({ type: 'ADD_LOG', payload: entry });
    dispatch({ type: 'UPDATE_LAST_ACTION', payload: { action: entry.action || entry.phase, ts: Date.now() } });
  };

  return (
    <div className="system-layout">
      <div className="system-grid">
        <PanelBox title="AGENT CONTROL">
          <div className="system-toggles">
            <div><Toggle value={state.agentRunning} onChange={() => dispatch({ type: 'TOGGLE_AGENT' })} label="EXECUTION ENGINE  :" /></div>
            <div><Toggle value={state.safeMode} onChange={() => dispatch({ type: 'TOGGLE_SAFE_MODE' })} label="SAFE MODE         :" /></div>
            <div><Toggle value={state.autoRebalance} onChange={() => dispatch({ type: 'TOGGLE_AUTO_REBALANCE' })} label="AUTO-REBALANCE    :" /></div>
            <div style={{ marginTop: '8px', display: 'flex', gap: '8px' }}>
              <button className="btn btn--danger" disabled={state.actionInFlight} onClick={() => setModal('PAUSE')}>
                [ PAUSE ALL EXECUTION ]
              </button>
              <button className="btn" onClick={handleForceTick} disabled={state.actionInFlight}>
                [ FORCE TICK NOW ]
              </button>
            </div>
          </div>
        </PanelBox>

        <PanelBox title="WALLET & NETWORK">
          <div className="system-wallet">
            <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>HEDERA NETWORK  : </span><span style={{ color: 'var(--color-success)' }}>[MAINNET]</span></div>
            <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>ACCOUNT ID      : </span><span style={{ color: 'var(--color-success)' }}>{state.walletId}</span></div>
            <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>HBAR BALANCE    : </span><span style={{ color: 'var(--color-white)' }}>{state.hbarBalance.toLocaleString()} HBAR  (${(state.hbarBalance * 0.084).toFixed(2)})</span></div>
            <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>USDC BALANCE    : </span><span style={{ color: 'var(--color-white)' }}>{state.usdcBalance.toLocaleString()} USDC</span></div>
            <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>GAS SAFETY LVL  : </span><ProgressBar value={0.75} /> <StatusTag status="OK" /></div>
          </div>
        </PanelBox>
      </div>

      <div className="system-grid">
        <PanelBox title="PRICE ALERT CONFIGURATION">
          <div className="alert-form">
            <div>
              <label>ASSET :</label>
              <select className="terminal-select">
                <option>HBAR/USDC ▼</option>
                <option>SAUCE/HBAR ▼</option>
              </select>
            </div>
            <div>
              <label>CONDITION :</label>
              <span onClick={() => setAlertCondition('above')} style={{ cursor: 'pointer', color: alertCondition === 'above' ? 'var(--color-white)' : 'var(--color-dim)' }}>
                {alertCondition === 'above' ? '(x)' : '( )'} ABOVE
              </span>
              {'    '}
              <span onClick={() => setAlertCondition('below')} style={{ cursor: 'pointer', color: alertCondition === 'below' ? 'var(--color-white)' : 'var(--color-dim)' }}>
                {alertCondition === 'below' ? '(x)' : '( )'} BELOW
              </span>
            </div>
            <div>
              <label>THRESHOLD :</label>
              <span style={{ color: 'var(--color-dim)' }}>&gt; $</span>
              <input className="terminal-input" type="text" value={alertThreshold} onChange={e => setAlertThreshold(e.target.value)} placeholder="0.000" />
            </div>
            <div>
              <label>ACTION :</label>
              <select className="terminal-select">
                <option>WITHDRAW_ALL ▼</option>
                <option>NARROW_RANGE ▼</option>
                <option>NOTIFY_ONLY ▼</option>
              </select>
            </div>
            <button className="btn" disabled={state.actionInFlight}>[ SAVE ALERT ]</button>
          </div>
        </PanelBox>

        <div>
          <PanelBox title="SYSTEM LOG EXPORT">
            <button className="btn" onClick={handleExportLog}>[ EXPORT EXECUTION LOG (.txt) ]</button>
          </PanelBox>

          <PanelBox title="ABOUT" doubleLine>
            <pre className="about-box">{`╔══════════════════════════════════════════════════╗
║  M.A.N.T.I.S. v1.0.0                            ║
║  Market Analysis & Network Tactical Integration  ║
║  © 2025 Elykid Private Limited                   ║
║  Network: Hedera Mainnet                         ║
║  Runtime: Hosted Cloud Service                   ║
╚══════════════════════════════════════════════════╝`}</pre>
          </PanelBox>
        </div>
      </div>

      {modal && (
        <ConfirmModal
          title="CONFIRM: PAUSE ALL"
          message="This will halt all agent execution immediately."
          variant="danger"
          onCancel={() => setModal(null)}
          onConfirm={() => {
            dispatch({ type: 'TOGGLE_AGENT' });
            setModal(null);
          }}
        />
      )}
    </div>
  );
}
