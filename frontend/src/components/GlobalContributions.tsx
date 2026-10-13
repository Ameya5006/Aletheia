import { fieldLabel } from './ui';
export function GlobalContributions({
  features,
}: {
  features: {
    field: string;
    mean_absolute_contribution: number;
    repeat_min: number;
    repeat_max: number;
  }[];
}) {
  const ordered = [...features].sort(
    (a, b) => b.mean_absolute_contribution - a.mean_absolute_contribution,
  );
  const max = Math.max(...ordered.map((f) => f.repeat_max), 0.000001);
  return (
    <div className="global-chart" aria-hidden="true">
      {ordered.map((f) => (
        <div className="contribution" key={f.field}>
          <span>{fieldLabel(f.field)}</span>
          <svg viewBox="0 0 200 24" preserveAspectRatio="none">
            <rect
              x="0"
              y="8"
              height="8"
              width={(f.mean_absolute_contribution / max) * 200}
              fill="var(--teal)"
            />
            <line
              x1={(f.repeat_min / max) * 200}
              x2={(f.repeat_max / max) * 200}
              y1="12"
              y2="12"
              stroke="var(--text)"
              strokeWidth="2"
            />
            <line
              x1={(f.repeat_min / max) * 200}
              x2={(f.repeat_min / max) * 200}
              y1="4"
              y2="20"
              stroke="var(--text)"
            />
            <line
              x1={(f.repeat_max / max) * 200}
              x2={(f.repeat_max / max) * 200}
              y1="4"
              y2="20"
              stroke="var(--text)"
            />
          </svg>
          <span className="mono">{f.mean_absolute_contribution.toFixed(6)}</span>
        </div>
      ))}
    </div>
  );
}
