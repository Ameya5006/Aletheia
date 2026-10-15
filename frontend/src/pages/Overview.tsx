import { Link } from 'react-router-dom';
import { useResource } from '../api/context';
import { healthSchema, modelSchema } from '../api/contracts';
import { PageHeading } from '../components/Shell';
import { Metric, Notice, Panel, Provenance, ResourceState, Status } from '../components/ui';
export function Overview() {
  const model = useResource('/models/current', modelSchema);
  const health = useResource('/health/ready', healthSchema);
  const m = model.value;
  return (
    <>
      <PageHeading
        title="Overview"
        description="Your workspace for case analysis, saved results and model evidence."
      />
      <Panel title="Start a new analysis">
        <p>
          No analysis is selected. Enter case data to receive a prediction, or open a saved analysis
          from your history.
        </p>
        <div className="actions">
          <Link className="button primary" to="/new-analysis">
            New Analysis
          </Link>
          <Link className="button secondary" to="/analyses">
            Analysis History
          </Link>
        </div>
      </Panel>
      <ResourceState loading={model.loading} error={model.error} retry={model.reload} />
      {m && (
        <div className="metric-grid">
          <Metric
            label="Model release"
            value={
              <>
                {m.evidence?.model_version} <Status>{m.data.approval_status}</Status>
              </>
            }
            caption={m.data.family}
          />
          <Metric
            label="Calibration"
            value={m.data.calibration}
            caption="Complete calibrated probability"
          />
          <Metric
            label="Service readiness"
            value={health.value?.data.status ?? (health.error ? 'Unavailable' : 'Loading?')}
            caption="API readiness, not separate service certification"
          />
          <Metric
            label="Audit integrity"
            value="Not published"
            caption="Hash-linked records; no full-chain verification endpoint"
          />
        </div>
      )}
      {m && !m.data.serving_available && (
        <Notice tone="warning">
          Live serving is unavailable. Published research evidence can remain readable.
        </Notice>
      )}
      <Panel title="Model evidence">
        <p>
          Inspect the frozen research evidence and its limitations separately from your analyses.
        </p>
        <ul className="readiness">
          <li>
            <Link to="/evidence/local">Published reference explanation</Link>
          </li>
          <li>
            <Link to="/evidence/stability">Model-level stability</Link>
          </li>
          <li>
            <Link to="/model-card">Model documentation</Link>
          </li>
        </ul>
      </Panel>
      <Provenance evidence={m?.evidence} />
    </>
  );
}
