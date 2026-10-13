import { fieldLabel, number, Panel, Notice } from './ui';
export type Contribution = { field: string; value?: string; contribution: number };
export function Contributions({
  features,
  compact = false,
}: {
  features: Contribution[];
  compact?: boolean;
}) {
  const sorted = [...features].sort((a, b) => Math.abs(b.contribution) - Math.abs(a.contribution));
  const shown = compact ? sorted.slice(0, 5) : sorted;
  const max = Math.max(...shown.map((f) => Math.abs(f.contribution)), 0.000001);
  return (
    <Panel title="What moves the estimate">
      <p className="small muted">
        Signed contributions to calibrated probability. Associations do not establish causality.
      </p>
      {shown.length === 0 && <Notice>No feature contributions have been published.</Notice>}
      <div className="contributions" aria-hidden="true">
        {shown.map((f) => (
          <div className="contribution" key={f.field}>
            <span>{fieldLabel(f.field)}</span>
            <div className="bar-track">
              <i
                className={f.contribution >= 0 ? 'raises' : 'lowers'}
                style={{ width: `${(Math.abs(f.contribution) / max) * 100}%` }}
              />
            </div>
            <span className="mono">
              {f.contribution >= 0 ? '+' : ''}
              {number(f.contribution, 6)}
            </span>
          </div>
        ))}
      </div>
      <details open={!compact}>
        <summary>Contribution values and directions</summary>
        <div className="table-scroll">
          <table>
            <caption>Source-field contributions in probability units</caption>
            <thead>
              <tr>
                <th>Source field</th>
                <th>Value</th>
                <th>Direction</th>
                <th>Contribution</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((f) => (
                <tr key={f.field}>
                  <th scope="row">{fieldLabel(f.field)}</th>
                  <td>{f.value ?? 'Not published'}</td>
                  <td>
                    {f.contribution > 0 ? 'Raises' : f.contribution < 0 ? 'Lowers' : 'Neutral'}
                  </td>
                  <td className="mono">
                    {f.contribution > 0 ? '+' : ''}
                    {number(f.contribution, 8)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </Panel>
  );
}
