import { useAgent } from '../../context/AgentContext';
import { ProgressBar } from '../../components/primitives/ProgressBar';
import { Sparkline } from '../../components/primitives/Sparkline';
import { StatusTag } from '../../components/primitives/StatusTag';
import { APY_HISTORY_7D } from '../../data/mockData';

export function VaultStatusPanel() {
  const { state } = useAgent();
  const vault = state.vaultData.find(v => v.id === state.activeVaultId) || state.vaultData[0];

  return (
    <div>
      <div>RANGE: <span style={{ color: 'var(--color-white)' }}>${vault.rangeLow.toFixed(3)} – ${vault.rangeHigh.toFixed(3)}</span></div>
      <div>POSIT: <ProgressBar value={vault.positionPct} /> {vault.inRange ? <StatusTag status="OK" /> : <StatusTag status="WARN" />}</div>
      <div>APY  : <span style={{ color: 'var(--color-white)' }}>{vault.apy24h}%</span></div>
      <div>REWRD: <span style={{ color: 'var(--color-white)' }}>${vault.rewardPending.toFixed(2)}</span> PENDING</div>
      <div style={{ marginTop: '4px' }}>
        <Sparkline data={APY_HISTORY_7D.slice(-48)} />
      </div>
    </div>
  );
}
