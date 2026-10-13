import { Link } from 'react-router-dom';
import { useResource } from '../api/context';
import { localSchema, globalSchema } from '../api/contracts';
import { Contributions } from '../components/Contributions';
import { GlobalContributions } from '../components/GlobalContributions';
import { PageHeading } from '../components/Shell';
import { fieldLabel, number, Notice, Panel, Provenance, ResourceState } from '../components/ui';
export function Explanation({ global = false }: { global?: boolean }) {
  const local = useResource(
    global ? undefined : '/explanations/local/synthetic-discharge-v1',
    localSchema,
  );
  const aggregate = useResource(global ? '/explanations/global' : undefined, globalSchema);
  const resource = global ? aggregate : local;
  return (
    <>
      <PageHeading
        title="Explanation"
        description="Understand the published estimate, its contributions and the limits of attribution."
      />
      <div className="tabs">
        <Link to="/evidence/local" aria-current={!global ? 'page' : undefined}>
          Local explanation
        </Link>
        <Link to="/evidence/global" aria-current={global ? 'page' : undefined}>
          Global evidence
        </Link>
      </div>
      <ResourceState
        loading={resource.loading}
        error={resource.error}
        retry={resource.reload}
        empty={!resource.value}
      />
      {local.value && (
        <>
          <Panel title="Baseline to calibrated probability">
            <div className="metric-grid">
              <div>
                <small>Sampled reference baseline</small>
                <p className="metric-value">{number(local.value.data.baseline, 8)}</p>
              </div>
              <div>
                <small>Baseline + signed contributions</small>
                <p className="metric-value">→ {number(local.value.data.probability, 8)}</p>
              </div>
            </div>
            <p>{local.value.data.method}</p>
            <Notice>
              These contributions already explain the complete calibrated probability. Calibration
              is not an additional feature contribution. Raw base score and calibration coefficients
              are not published by this endpoint.
            </Notice>
          </Panel>
          <Contributions features={local.value.data.features} />
          <Panel title="Source-feature grouping">
            <p>
              Published contributions group by original source field. Transformed-column lineage is
              not supplied by this API projection.
            </p>
            <p>{local.value.data.limitations}</p>
          </Panel>
        </>
      )}
      {aggregate.value && (
        <Panel title="Global contribution evidence">
          <p>{aggregate.value.data.population}</p>
          <p className="small">
            {aggregate.value.data.sample_size_per_repeat} encounters per repeat ·{' '}
            {aggregate.value.data.seeds.length} seeded repeats. Repeat ranges are descriptive, not
            confidence intervals.
          </p>
          <GlobalContributions features={aggregate.value.data.features} />
          <div className="table-scroll">
            <table>
              <caption>Mean absolute contributions in calibrated-probability units</caption>
              <thead>
                <tr>
                  <th>Source field</th>
                  <th>Mean absolute contribution</th>
                  <th>Repeat range</th>
                </tr>
              </thead>
              <tbody>
                {[...aggregate.value.data.features]
                  .sort((a, b) => b.mean_absolute_contribution - a.mean_absolute_contribution)
                  .map((f) => (
                    <tr key={f.field}>
                      <th scope="row">{fieldLabel(f.field)}</th>
                      <td className="mono">{number(f.mean_absolute_contribution, 8)}</td>
                      <td className="mono">
                        {number(f.repeat_min, 8)}–{number(f.repeat_max, 8)}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
          <Notice>{aggregate.value.data.limitations}</Notice>
        </Panel>
      )}
      <Provenance evidence={resource.value?.evidence} />
    </>
  );
}
