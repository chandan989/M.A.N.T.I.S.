import { useAgent } from '../../context/AgentContext';
import { PanelBox } from '../../components/primitives/PanelBox';
import { SkillPanel } from './SkillPanel';
import { RiskProfileSelector } from './RiskProfileSelector';
import './Skills.css';

export default function Skills() {
  const { state } = useAgent();

  return (
    <div>
      <div className="skills-layout">
        <SkillPanel
          name="SENTRY"
          version="1.0.0"
          sources="Twitter/X, CryptoPanic, Polymarket, Hedera HCS"
          lastRun="00:47 ago"
          nextRun="00:13"
          details={
            <div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>SCORE   : </span><span style={{ color: 'var(--color-white)' }}>{state.sentryData.score.toFixed(2)}</span> ({state.sentryData.label})</div>
              <div style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>SIGNALS :</div>
              {state.sentryData.signals.map((s, i) => (
                <div key={i} style={{ color: 'var(--color-dim)', paddingLeft: '10px' }}>&gt; {s}</div>
              ))}
            </div>
          }
        />
        <SkillPanel
          name="ORACLE"
          version="1.0.0"
          sources="Hedera Mirror Node, SaucerSwap API, CoinGecko"
          lastRun="00:12 ago"
          nextRun="00:03"
          details={
            <div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>PAIR    : </span><span style={{ color: 'var(--color-white)' }}>{state.oracleData.pair}</span></div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>PRICE   : </span><span style={{ color: 'var(--color-white)' }}>${state.oracleData.price.toFixed(4)}</span></div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>VOLA    : </span><span style={{ color: 'var(--color-white)' }}>{state.oracleData.volatility.toFixed(2)}</span></div>
            </div>
          }
        />
        <SkillPanel
          name="HEDERA"
          version="1.0.0"
          sources="Hedera SDK, Mirror Node REST API"
          lastRun="00:02 ago"
          nextRun="00:08"
          details={
            <div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>ACCOUNT : </span><span style={{ color: 'var(--color-success)' }}>{state.walletId}</span></div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>BALANCE : </span><span style={{ color: 'var(--color-white)' }}>{state.hbarBalance.toLocaleString()} HBAR</span></div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>TX/24H  : </span><span style={{ color: 'var(--color-white)' }}>12</span></div>
            </div>
          }
        />
        <SkillPanel
          name="MEMORY"
          version="1.0.0"
          sources="Local Vector Store, Execution History"
          lastRun="00:47 ago"
          nextRun="00:13"
          details={
            <div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>ENTRIES : </span><span style={{ color: 'var(--color-white)' }}>1,247</span></div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>STORAGE : </span><span style={{ color: 'var(--color-white)' }}>4.2 MB</span></div>
              <div><span style={{ color: 'var(--color-dim)', textTransform: 'uppercase' }}>RECALL  : </span><span style={{ color: 'var(--color-white)' }}>Last 30 decisions cached</span></div>
            </div>
          }
        />
      </div>

      <div style={{ marginTop: '12px' }}>
        <PanelBox title="RISK CONFIGURATION">
          <RiskProfileSelector />
        </PanelBox>
      </div>
    </div>
  );
}
