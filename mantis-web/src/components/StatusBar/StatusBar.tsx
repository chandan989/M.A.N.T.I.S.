import { useAgent } from '../../context/AgentContext';
import { useWallet } from '../../context/WalletContext';
import { useLiveTick } from '../../hooks/useLiveTick';

export function StatusBar() {
  const { state } = useAgent();
  const { wallet, status: walletStatus } = useWallet();
  const tick = useLiveTick(state.lastActionTs);

  const walletDisplay =
    walletStatus === 'connected' && wallet
      ? wallet.accountId
      : walletStatus === 'connecting'
        ? 'CONNECTING...'
        : 'NOT CONNECTED';

  const walletColor =
    walletStatus === 'connected'
      ? 'var(--color-success)'
      : walletStatus === 'connecting'
        ? 'var(--color-primary)'
        : 'var(--color-error)';

  return (
    <div style={{
      position: 'fixed',
      bottom: 0,
      left: 0,
      right: 0,
      background: 'var(--color-bg)',
      borderTop: '1px solid var(--color-dim)',
      padding: '4px 16px',
      fontFamily: 'var(--font-mono)',
      fontSize: '12px',
      zIndex: 100,
      display: 'flex',
      gap: '8px',
    }}>
      <span>SYS.MODE: <span style={{ color: state.agentRunning ? 'var(--color-success)' : 'var(--color-error)' }}>[{state.agentRunning ? 'ACTIVE' : 'PAUSED'}]</span></span>
      <span style={{ color: 'var(--color-dim)' }}>|</span>
      <span>NET: <span style={{ color: wallet?.network === 'testnet' ? 'var(--color-primary)' : 'var(--color-success)' }}>[{wallet?.network?.toUpperCase() ?? 'MAINNET'}]</span></span>
      <span style={{ color: 'var(--color-dim)' }}>|</span>
      <span>WALLET: <span style={{ color: walletColor }}>{walletDisplay}</span></span>
      <span style={{ color: 'var(--color-dim)' }}>|</span>
      <span>VAULT: <span style={{ color: 'var(--color-success)' }}>{state.activeVaultId}</span></span>
      <span style={{ color: 'var(--color-dim)' }}>|</span>
      <span>LAST ACT: <span style={{ color: 'var(--color-white)' }}>{state.lastAction}</span></span>
      <span style={{ color: 'var(--color-dim)' }}>|</span>
      <span>TICK: <span style={{ color: 'var(--color-white)' }}>{tick} ago</span></span>
      <span style={{ color: 'var(--color-dim)' }}>|</span>
      <span className="cursor">█</span>
    </div>
  );
}
