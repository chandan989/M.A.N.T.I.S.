import { TX_HISTORY } from '../../data/mockData';
import { PanelBox } from '../../components/primitives/PanelBox';
import { StatusTag } from '../../components/primitives/StatusTag';

export function TxHistoryTable() {
  return (
    <PanelBox title="TRANSACTION HISTORY">
      <table className="tx-table">
        <thead>
          <tr>
            <th>TX HASH</th>
            <th>ACTION</th>
            <th>STATUS</th>
            <th>VALUE</th>
            <th>AGE</th>
          </tr>
        </thead>
        <tbody>
          {TX_HISTORY.map((tx, i) => (
            <tr key={i}>
              <td><span className="tx-hash">{tx.hash.slice(0, 8)}...{tx.hash.slice(-4)}</span></td>
              <td>{tx.action}</td>
              <td><StatusTag status={tx.status} /></td>
              <td style={{ color: 'var(--color-white)' }}>{tx.value}</td>
              <td style={{ color: 'var(--color-dim)' }}>{tx.age}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </PanelBox>
  );
}
