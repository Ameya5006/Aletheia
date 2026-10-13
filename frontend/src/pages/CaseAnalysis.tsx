import { useContext, useRef, useState } from 'react';
import { ApiError } from '../api/client';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ApiContext, useResource } from '../api/context';
import {
  CASE_ID,
  SCHEMA,
  casesSchema,
  modelSchema,
  localSchema,
  predictionSchema,
  sameEvidence,
} from '../api/contracts';
import { useAuth } from '../auth/session';
import { PageHeading } from '../components/Shell';
import {
  fieldLabel,
  Notice,
  Panel,
  Probability,
  Provenance,
  ResourceState,
} from '../components/ui';
export function CaseAnalysis() {
  const { id } = useParams();
  const auth = useAuth();
  return <CaseContent key={`${id ?? 'demo'}:${auth.token ?? 'public'}`} />;
}
function CaseContent() {
  const { id } = useParams();
  const auth = useAuth();
  const api = useContext(ApiContext);
  const navigate = useNavigate();
  const cases = useResource('/demo/cases', casesSchema);
  const model = useResource('/models/current', modelSchema);
  const local = useResource('/explanations/local/' + CASE_ID, localSchema);
  const persisted = useResource(
    id ? '/predictions/' + encodeURIComponent(id) : undefined,
    predictionSchema,
    true,
  );
  const pending = useRef<{ key: string; version: string } | undefined>(undefined);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>();
  const m = model.value;
  const caseData = cases.value?.data[0];
  const prediction = persisted.value;
  const evidence = prediction?.evidence ?? local.value?.evidence;
  const consistent = Boolean(
    m?.evidence &&
    cases.value?.evidence &&
    local.value?.evidence &&
    [
      cases.value.evidence,
      local.value.evidence,
      ...(prediction?.evidence ? [prediction.evidence] : []),
    ].every((e) => sameEvidence(e, m.evidence)),
  );
  async function predict() {
    if (
      !m?.evidence ||
      busy ||
      !consistent ||
      !m.data.serving_available ||
      !auth.token ||
      !auth.roles.some((r) => ['engineer', 'reviewer', 'administrator'].includes(r))
    )
      return;
    setBusy(true);
    setError(undefined);
    pending.current ??= { key: crypto.randomUUID(), version: m.evidence.model_version };
    try {
      const result = await api.request('/predictions', predictionSchema, {
        body: { schema_version: SCHEMA, case_id: CASE_ID, model_version: pending.current.version },
        key: pending.current.key,
        private: true,
      });
      pending.current = undefined;
      navigate('/predictions/' + result.data.prediction_id);
    } catch (failure) {
      setError(failure);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading
        title="Case Analysis"
        description="A fixed synthetic encounter. Read-only context and calibrated evidence."
      />
      <ResourceState
        loading={cases.loading || model.loading}
        error={cases.error ?? model.error}
        retry={() => {
          cases.reload();
          model.reload();
        }}
      />
      {id && (
        <ResourceState
          loading={persisted.loading}
          error={persisted.error}
          retry={persisted.reload}
        />
      )}
      <div className="two-columns">
        <Panel title="Case context">
          <Notice>Inputs are fixed on the server and cannot be edited.</Notice>
          {caseData ? (
            <>
              <p className="mono">{caseData.id}</p>
              <dl className="facts">
                {Object.entries(caseData.features).map(([field, value]) => (
                  <div key={field}>
                    <dt>{fieldLabel(field)}</dt>
                    <dd>{String(value ?? 'Missing')}</dd>
                  </div>
                ))}
              </dl>
            </>
          ) : (
            <p>No case context is available.</p>
          )}
        </Panel>
        <div>
          <Panel title={id ? 'Persisted prediction' : 'Published synthetic estimate'}>
            {!consistent && (
              <Notice tone="warning">
                Evidence identities are loading, unavailable or inconsistent. Submission is
                disabled.
              </Notice>
            )}
            <ResourceState loading={local.loading} error={local.error} retry={local.reload} />
            {consistent && (prediction || !id) && (
              <Probability
                probability={prediction?.data.probability ?? local.value!.data.probability}
                threshold={prediction?.data.threshold ?? m?.data.threshold}
              />
            )}
            <dl className="facts">
              <div>
                <dt>Model version</dt>
                <dd>{evidence?.model_version ?? 'Not available'}</dd>
              </div>
              <div>
                <dt>Prediction timestamp</dt>
                <dd>{prediction ? <time>{prediction.data.created_at}</time> : 'Not persisted'}</dd>
              </div>
              {prediction && (
                <>
                  <div>
                    <dt>Prediction ID</dt>
                    <dd className="mono">{prediction.data.prediction_id}</dd>
                  </div>
                  <div>
                    <dt>Explanation reference</dt>
                    <dd className="mono">{prediction.data.explanation_ref}</dd>
                  </div>
                </>
              )}
            </dl>
            <Link to="/evidence/local">Inspect explanation →</Link>
          </Panel>
          <Panel title="Audited inference">
            {auth.token ? (
              <>
                <p>
                  Run the approved synthetic case and persist its prediction with an audit event.
                </p>
                <button
                  className="button primary"
                  disabled={
                    busy ||
                    !consistent ||
                    !m?.data.serving_available ||
                    !auth.roles.some((r) => ['engineer', 'reviewer', 'administrator'].includes(r))
                  }
                  onClick={() => void predict()}
                >
                  {busy
                    ? 'Submitting…'
                    : pending.current
                      ? 'Retry same prediction'
                      : 'Create audited prediction'}
                </button>
              </>
            ) : (
              <Link className="button primary" to="/sign-in">
                Sign in to request inference
              </Link>
            )}
            <ResourceState loading={false} error={error} retry={() => void predict()} />
            {error instanceof ApiError && error.status === 409 && (
              <button
                className="button secondary"
                onClick={() => {
                  pending.current = undefined;
                  setError(undefined);
                  model.reload();
                  cases.reload();
                  local.reload();
                }}
              >
                Refresh evidence and start a new submission
              </button>
            )}
            {pending.current && Boolean(error) && (
              <p className="small">
                Retry preserves the same submission identity. A timeout does not prove the
                transaction failed.
              </p>
            )}
            {prediction && (
              <p>
                <Link to={'/predictions/' + prediction.data.prediction_id + '/review'}>
                  Review this prediction →
                </Link>{' '}
                ·{' '}
                <Link to={'/audit-history/' + prediction.data.event_id}>
                  Prediction audit event →
                </Link>
              </p>
            )}
          </Panel>
        </div>
      </div>
      <Provenance evidence={evidence} />
    </>
  );
}
