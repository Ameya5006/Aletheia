import { Link } from 'react-router-dom';
import { useResource } from '../api/context';
import { healthSchema, modelSchema, localSchema, sameEvidence } from '../api/contracts';
import { Contributions } from '../components/Contributions';
import { PageHeading } from '../components/Shell';
import {
  Metric,
  Notice,
  Panel,
  Probability,
  Provenance,
  ResourceState,
  Status,
} from '../components/ui';
export function Overview() {
  const model = useResource('/models/current', modelSchema);
  const health = useResource('/health/ready', healthSchema);
  const local = useResource('/explanations/local/synthetic-discharge-v1', localSchema);
  const m = model.value;
  const e = local.value;
  const consistent = !m || !e || sameEvidence(m.evidence, e.evidence);
  return (
    <>
      <PageHeading
        title="Overview"
        description="Governance status and published evidence for the fixed synthetic case."
      />
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
            value={health.value?.data.status ?? (health.error ? 'Unavailable' : 'Loading…')}
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
      {!consistent && (
        <Notice tone="warning">
          Model and explanation identities differ. Refresh evidence before continuing.
        </Notice>
      )}
      <div className="overview-case">
        <div className="case-intro">
          <div className="eyebrow">THE CASE / SYNTHETIC</div>
          <h2>
            One estimate.
            <br />
            Evidence at every step.
          </h2>
          <p>
            Trace the fixed discharge demonstration from calibrated probability to a considered
            human review.
          </p>
          <p className="mono small">synthetic-discharge-v1</p>
          <Link className="button primary" to="/demo">
            Open case <span aria-hidden="true">→</span>
          </Link>
        </div>
        <div className="case-estimate">
          <ResourceState loading={local.loading} error={local.error} retry={local.reload} />
          {e && consistent && (
            <>
              <Probability probability={e.data.probability} threshold={m?.data.threshold} />
              <p className="small muted">
                Published synthetic research example. A persisted prediction requires authenticated
                inference.
              </p>
            </>
          )}
        </div>
      </div>
      <Panel title="From estimate to accountability">
        <div className="workflow">
          {[
            ['Case', '/demo', 'Fixed inputs'],
            ['Explanation', '/evidence/local', 'Signed contributions'],
            ['Stability', '/evidence/stability', 'Recording sensitivity'],
            ['Subgroups', '/evidence/subgroups', 'Support and uncertainty'],
            ['Review', '/review', 'Coded decision'],
            ['Audit trail', '/audit-history', 'Committed events'],
          ].map(([title, path, note], i) => (
            <Link key={title} to={path!}>
              <span className="eyebrow">0{i + 1} →</span>
              <strong>{title}</strong>
              <small>{note}</small>
            </Link>
          ))}
        </div>
      </Panel>
      <div className="two-columns">
        {e && consistent && <Contributions features={e.data.features} compact />}
        <Panel title="Review readiness">
          <p>Confirm the evidence and its limitations before recording a review.</p>
          <ul className="readiness">
            <li>
              <Link to="/evidence/local">Prediction and explanation →</Link>
            </li>
            <li>
              <Link to="/evidence/stability">Reliability evidence →</Link>
            </li>
            <li>
              <Link to="/model-card">Model documentation →</Link>
            </li>
          </ul>
          <p className="small muted">Review status is shown only for a persisted prediction.</p>
          <Link className="text-link" to="/review">
            Open review workflow →
          </Link>
        </Panel>
      </div>
      <Provenance evidence={m?.evidence} />
    </>
  );
}
