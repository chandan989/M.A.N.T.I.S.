import { useAgent } from '../../context/AgentContext';
import { PanelBox } from '../../components/primitives/PanelBox';
import { StatusTag } from '../../components/primitives/StatusTag';
import { ProgressBar } from '../../components/primitives/ProgressBar';

export function VaultDetailPanel() {
  const { state } = useAgent();
  const vault = state.vaultData.find(v => v.id === state.activeVaultId) || state.vaultData[0];

  return (
    <PanelBox title={`VAULT: ${vault.name} — ${vault.id}`}>
      <div className="vault-detail-grid">
        <div><span className="vault-label">STRATEGY</span>: <span style={{ color: 'var(--color-white)' }}>{vault.strategy}</span></div>
        <div><span className="vault-label">PROTOCOL</span>: <span style={{ color: 'var(--color-white)' }}>{vault.protocol}</span></div>
        <div><span className="vault-label">RANGE LOW</span>: <span style={{ color: 'var(--color-white)' }}>${vault.rangeLow.toFixed(3)}</span></div>
        <div><span className="vault-label">RANGE HIGH</span>: <span style={{ color: 'var(--color-white)' }}>${vault.rangeHigh.toFixed(3)}</span></div>
        <div><span className="vault-label">IN RANGE</span>: {vault.inRange ? <StatusTag status="OK" /> : <StatusTag status="FAIL" />}</div>
        <div><span className="vault-label">POSITION</span>: <ProgressBar value={vault.positionPct} /></div>
        <div><span className="vault-label">APY 24H</span>: <span style={{ color: 'var(--color-white)' }}>{vault.apy24h}%</span></div>
        <div><span className="vault-label">APY 7D</span>: <span style={{ color: 'var(--color-white)' }}>{vault.apy7d}%</span></div>
        <div><span className="vault-label">REWRD PEND</span>: <span style={{ color: 'var(--color-white)' }}>${vault.rewardPending.toFixed(2)} HBAR</span></div>
        <div><span className="vault-label">LAST HARV</span>: <span style={{ color: 'var(--color-white)' }}>{vault.lastHarvest}</span></div>
        <div><span className="vault-label">DEPOSITED</span>: <span style={{ color: 'var(--color-white)' }}>${vault.deposited.toLocaleString()}</span></div>
        <div><span className="vault-label">P&L ALL-TM</span>: <span style={{ color: vault.pnlAllTime >= 0 ? 'var(--color-success)' : 'var(--color-error)' }}>+${vault.pnlAllTime.toFixed(2)}</span></div>
      </div>
    </PanelBox>
  );
}
