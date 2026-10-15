import { useContext, useRef, useState } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';
import { ApiContext, useResource } from '../api/context';
import { ApiError } from '../api/client';
import {
  SCHEMA,
  pageSchema,
  predictionSchema,
  reviewSchema,
  reviewRequestSchema,
  type ReviewRequest,
  type Result,
  type Review,
} from '../api/contracts';
import { useAuth } from '../auth/session';
import { PageHeading } from '../components/Shell';
import { fieldLabel, Notice, Panel, Provenance, ResourceState } from '../components/ui';
const reviewsPage = pageSchema(reviewSchema);
const checklist = [
  ['Prediction and explanation', '/evidence/local'],
  ['Reliability and subgroup limits', '/evidence/stability'],
  ['Model documentation', '/model-card'],
];
export function ReviewPage() {
  const { id } = useParams();
  const auth = useAuth();
  return <ReviewForm key={`${id ?? 'lookup'}:${auth.token ?? 'public'}`} />;
}
function ReviewForm() {
  const auth = useAuth();
  const { id } = useParams();
  const api = useContext(ApiContext);
  const navigate = useNavigate();
  const [lookup, setLookup] = useState('');
  const [checked, setChecked] = useState<string[]>([]);
  const [decision, setDecision] = useState<ReviewRequest['decision']>('acknowledged');
  const [reason, setReason] = useState<ReviewRequest['reason_code'] | ''>('');
  const [revision, setRevision] = useState('0');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>();
  const [validation, setValidation] = useState('');
  const [success, setSuccess] = useState<Result<Review>>();
  const pending = useRef<{ key: string; body: ReviewRequest } | undefined>(undefined);
  const allowed = auth.roles.includes('reviewer');
  const prediction = useResource(
    auth.token && id ? '/predictions/' + encodeURIComponent(id) : undefined,
    predictionSchema,
    true,
  );
  const history = useResource(
    auth.token && id ? '/predictions/' + encodeURIComponent(id) + '/reviews' : undefined,
    reviewsPage,
    true,
  );
  async function submit() {
    if (!id || !allowed || busy) return;
    setValidation('');
    const parsed = reviewRequestSchema.safeParse({
      schema_version: SCHEMA,
      decision,
      reason_code: reason,
      expected_revision: Number(revision),
    });
    if (!parsed.success || !revision.trim() || checked.length !== checklist.length) {
      setValidation(
        'Check each evidence item, select a required coded reason and enter a nonnegative integer revision.',
      );
      return;
    }
    pending.current ??= { key: crypto.randomUUID(), body: parsed.data };
    setBusy(true);
    setError(undefined);
    setSuccess(undefined);
    try {
      const result = await api.request(
        '/predictions/' + encodeURIComponent(id) + '/reviews',
        reviewSchema,
        { body: pending.current.body, key: pending.current.key, private: true },
      );
      setSuccess(result);
      setRevision(String(result.data.revision));
      pending.current = undefined;
      history.reload();
    } catch (failure) {
      setError(failure);
    } finally {
      setBusy(false);
    }
  }
  function refreshConflict() {
    pending.current = undefined;
    setError(undefined);
    prediction.reload();
    history.reload();
  }
  return (
    <>
      <PageHeading
        title="Review"
        description="Record a considered evidence decision against a persisted prediction."
      />
      {!auth.token ? (
        <Notice>
          <Link to="/sign-in">Sign in to access review history and submission.</Link>
        </Notice>
      ) : !id ? (
        <Panel title="Select a persisted prediction">
          <p>Run a new analysis, open Analysis History, or enter an authorized prediction ID.</p>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              if (/^[0-9a-f-]{36}$/i.test(lookup)) navigate('/predictions/' + lookup + '/review');
            }}
          >
            <label className="form-field">
              Prediction ID
              <input
                value={lookup}
                onChange={(e) => setLookup(e.target.value)}
                required
                pattern="[0-9a-fA-F-]{36}"
              />
            </label>
            <button className="button primary">Open review</button>
          </form>
          <p>
            <Link to="/new-analysis">New Analysis →</Link>
          </p>
        </Panel>
      ) : (
        <>
          <ResourceState
            loading={prediction.loading || history.loading}
            error={prediction.error ?? history.error}
            retry={() => {
              prediction.reload();
              history.reload();
            }}
          />
          {!allowed && (
            <Notice tone="warning">
              Clinical Reviewer permission is required to submit. Administrator and engineer roles
              do not grant reviewer permission.
            </Notice>
          )}
          {prediction.value && (
            <div className="review-grid">
              <Panel title="Evidence checklist and decision">
                <p className="mono small">{prediction.value.data.prediction_id}</p>
                <p>
                  Model {prediction.value.evidence?.model_version} · explanation reference{' '}
                  {prediction.value.data.explanation_ref ?? 'Stored with this analysis'}
                </p>
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    void submit();
                  }}
                >
                  <fieldset disabled={!allowed || busy || Boolean(pending.current)}>
                    <legend>Confirm evidence reviewed</legend>
                    {checklist.map(([label, path]) => (
                      <div className="check-row" key={label}>
                        <label>
                          <input
                            type="checkbox"
                            checked={checked.includes(label!)}
                            onChange={(e) =>
                              setChecked((current) =>
                                e.target.checked
                                  ? [...current, label!]
                                  : current.filter((v) => v !== label),
                              )
                            }
                          />
                          {label}
                        </label>
                        <Link
                          to={
                            label === 'Prediction and explanation' &&
                            prediction.value?.data.case_id === 'entered-case-v1'
                              ? '/analyses/' + prediction.value?.data.prediction_id
                              : path!
                          }
                        >
                          Inspect →
                        </Link>
                      </div>
                    ))}
                    <fieldset>
                      <legend>Decision</legend>
                      {['acknowledged', 'needs_investigation', 'dismissed_demo'].map((d) => (
                        <label className="radio-card" key={d}>
                          <input
                            type="radio"
                            name="decision"
                            checked={decision === d}
                            onChange={() => setDecision(d as ReviewRequest['decision'])}
                          />
                          {fieldLabel(d)}
                        </label>
                      ))}
                    </fieldset>
                    <label className="form-field">
                      Required coded reason
                      <select
                        value={reason}
                        onChange={(e) =>
                          setReason(e.target.value as ReviewRequest['reason_code'] | '')
                        }
                        required
                      >
                        <option value="">Select reason</option>
                        {['evidence_reviewed', 'limitations_noted', 'identity_issue'].map((r) => (
                          <option key={r} value={r}>
                            {fieldLabel(r)}
                          </option>
                        ))}
                      </select>
                    </label>
                    <p className="small muted">
                      The approved API accepts coded reasons only. Free-text comments are not
                      collected.
                    </p>
                    <label className="form-field">
                      Your expected revision
                      <input
                        type="number"
                        min="0"
                        step="1"
                        required
                        value={revision}
                        onChange={(e) => setRevision(e.target.value)}
                      />
                    </label>
                    <p className="small muted">
                      Revisions are per prediction and reviewer. Use 0 for your first review.
                      History is redacted; do not infer your revision from another reviewer’s entry.
                    </p>
                  </fieldset>
                  {validation && <p role="alert">{validation}</p>}
                  <button
                    className="button primary"
                    disabled={!allowed || busy || history.loading || Boolean(history.error)}
                  >
                    {busy
                      ? 'Submitting…'
                      : pending.current
                        ? 'Retry same review'
                        : 'Submit coded review'}
                  </button>
                </form>
                <ResourceState loading={false} error={error} retry={() => void submit()} />
                {error instanceof ApiError && error.status === 409 && (
                  <button className="button secondary" onClick={refreshConflict}>
                    Refresh history and start a new submission
                  </button>
                )}
                {pending.current && Boolean(error) && (
                  <Notice>
                    The outcome is unconfirmed. The retry uses the same body and idempotency key.
                  </Notice>
                )}
                {success && (
                  <div role="status" className="notice success">
                    Review persisted · revision {success.data.revision}.{' '}
                    <Link to={'/audit-history/' + success.data.event_id}>
                      Inspect linked audit event →
                    </Link>
                  </div>
                )}
              </Panel>
              <Panel title="Review history">
                {history.value?.data.items.length === 0 && <p>No reviews have been recorded.</p>}
                <ol className="timeline">
                  {history.value?.data.items.map((item) => (
                    <li key={item.review_id}>
                      <time>{item.created_at}</time>
                      <h3>{fieldLabel(item.decision)}</h3>
                      <p>
                        {fieldLabel(item.reason_code)} · revision {item.revision}
                      </p>
                      <Link to={'/audit-history/' + item.event_id}>Audit evidence →</Link>
                    </li>
                  ))}
                </ol>
                <Notice>
                  Each review is an appended evidence decision, not a clinical approval.
                </Notice>
              </Panel>
            </div>
          )}
          <Provenance evidence={prediction.value?.evidence} />
        </>
      )}
    </>
  );
}
