import { useAgent } from '../../context/AgentContext';
import { Sparkline } from '../../components/primitives/Sparkline';
import { StatusTag } from '../../components/primitives/StatusTag';

export function OracleFeedPanel() {
  const { state } = useAgent();
  const { oracleData } = state;
  const priceColor = oracleData.change1h > 0 ? 'var(--color-success)' : 'var(--color-error)';

  return (
    <div>
      <div>PAIR : <span style={{ color: 'var(--color-white)' }}>{oracleData.pair}</span></div>
      <div>PRIC : <span style={{ color: priceColor }}>${oracleData.price.toFixed(4)}</span></div>
      <div>VOLA : <span style={{ color: 'var(--color-white)' }}>{oracleData.volatility.toFixed(2)}</span> {oracleData.volatility > 0.7 ? <StatusTag status="WARN" /> : <StatusTag status="OK" />}</div>
      <div>TREN : <Sparkline data={oracleData.trend} /></div>
    </div>
  );
}
