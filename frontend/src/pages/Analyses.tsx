import { useContext, useRef, useState } from 'react';
import { Link, useLocation, useNavigate, useParams } from 'react-router-dom';
import { ApiContext, useResource } from '../api/context';
import { ApiError, errorCopy } from '../api/client';
import {
  analysesSchema,
  analysisSchema,
  inputFieldsSchema,
  type Analysis,
  type InputField,
} from '../api/analyses';
import { modelSchema } from '../api/contracts';
import { useAuth } from '../auth/session';
import { PageHeading } from '../components/Shell';
import { displayText, Panel, Probability, ResourceState } from '../components/ui';

function validation(field: InputField, value: string | undefined) {
  if (!value) return 'Choose or enter a value.';
  if (field.control === 'select')
    return field.options.some((o) => o.value === value) ? undefined : 'Choose a listed option.';
  const number = Number(value);
  return !/^\d+$/.test(value) ||
    !Number.isSafeInteger(number) ||
    number < field.minimum! ||
    number > field.maximum!
    ? `Enter a whole number from ${field.minimum} to ${field.maximum}.`
    : undefined;
}
function Access() {
  return (
    <p role="alert">
      An authorized provisioned identity is required.{' '}
      <Link to="/local-session">Connect provisioned identity</Link>. Login and Signup remain future
      scope.
    </p>
  );
}
function Result({
  result,
  onLoad,
  onSave,
  busy,
}: {
  result: Analysis;
  onLoad: () => void;
  onSave: () => void;
  busy: boolean;
}) {
  return (
    <>
      <Panel title="Prediction Result">
        <Probability probability={result.probability} threshold={result.threshold} />
        <p>{result.category}</p>
        <p>
          Save state: <strong>{result.saved ? 'Saved' : 'Not saved to Analysis History'}</strong>
        </p>
        <dl className="facts">
          {Object.entries({
            'Model version': result.model_version,
            'Model SHA-256': result.model_sha256,
            'Release SHA-256': result.release_sha256,
            'Evidence SHA-256': result.evidence_sha256,
            'Prediction identifier': result.prediction_id,
            'Audit identifier': result.event_id,
            Created: result.created_at,
            'Review state': displayText(result.review_state),
          }).map(([k, v]) => (
            <div key={k}>
              <dt>{k}</dt>
              <dd className="mono">{v}</dd>
            </div>
          ))}
        </dl>
        <button className="button primary" onClick={onSave} disabled={busy || result.saved}>
          {busy ? 'Saving…' : 'Save Analysis'}
        </button>{' '}
        <button className="button secondary" onClick={onLoad} disabled={busy}>
          Load inputs into New Analysis
        </button>
        <p>
          <Link to={'/analyses/' + result.prediction_id}>Open stored result</Link> ·{' '}
          <Link to={'/predictions/' + result.prediction_id + '/review'}>Review Analysis</Link>
        </p>
      </Panel>
      <Panel title="Explanation evidence">
        <p>
          {result.explanation.method}. {result.explanation.reference_scope}.
        </p>
        <p>
          Reference probability: <span className="mono">{result.explanation.baseline}</span>.
          Contributions are probability changes relative to this reference.
        </p>
        {(['raises', 'lowers'] as const).map((direction) => (
          <div className="table-scroll" key={direction}>
            <table>
              <caption>
                {direction === 'raises'
                  ? 'Factors increasing the output'
                  : 'Factors decreasing the output'}
              </caption>
              <thead>
                <tr>
                  <th>Field</th>
                  <th>Contribution</th>
                </tr>
              </thead>
              <tbody>
                {result.explanation.features
                  .filter((f) => f.direction === direction)
                  .map((f) => (
                    <tr key={f.field}>
                      <th scope="row">{f.label}</th>
                      <td className="mono">{f.contribution}</td>
                    </tr>
                  ))}
              </tbody>
            </table>
            {!result.explanation.features.some((f) => f.direction === direction) && (
              <p>
                No {direction === 'raises' ? 'increasing' : 'decreasing'} contribution relative to
                this reference.
              </p>
            )}
          </div>
        ))}
        <details>
          <summary>All contribution values and reference inputs</summary>
          <pre>
            {JSON.stringify(
              {
                features: result.explanation.features,
                reference: result.explanation.reference_inputs,
              },
              null,
              2,
            )}
          </pre>
        </details>
        <p className="small">{result.explanation.limitations}</p>
      </Panel>
      <Panel title="Model-level stability evidence">
        <p>
          Frozen study: {result.stability.evidence.comparisons} recording comparisons; mean top-3
          overlap {result.stability.evidence.all.top_k_overlap.mean}. No per-case stability score is
          available.
        </p>
        <Link to="/evidence/stability">Inspect the frozen stability study</Link>
        <p className="small">{result.stability.evidence.limitations}</p>
      </Panel>
      <Panel title="Stored inputs and review history">
        <dl className="facts">
          {result.explanation.features.map((f) => (
            <div key={f.field}>
              <dt>{f.label}</dt>
              <dd>{result.inputs[f.field]}</dd>
            </div>
          ))}
        </dl>
        <p>
          {result.review_history.length} recorded review revisions. Original inputs and model output
          are immutable.
        </p>
        {result.review_history.map((r) => (
          <p key={r.review_id}>
            {r.created_at} · {displayText(r.decision)} · revision {r.revision}
          </p>
        ))}
      </Panel>
      <p className="small">
        Historical model evidence; threshold 0.5 is descriptive and has very low recall. No clinical
        validation or individual outcome guarantee.
      </p>
    </>
  );
}

export function NewAnalysis() {
  const location = useLocation();
  const auth = useAuth();
  return <AnalysisForm key={location.key + String(Boolean(auth.token))} />;
}
function AnalysisForm() {
  const api = useContext(ApiContext);
  const auth = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const mapping = useResource(auth.token ? '/analyses/schema' : undefined, inputFieldsSchema, true);
  const model = useResource(auth.token ? '/models/current' : undefined, modelSchema);
  const [inputs, setInputs] = useState<Record<string, string>>(() => location.state?.inputs ?? {});
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [result, setResult] = useState<Analysis>();
  const [error, setError] = useState<unknown>();
  const [busy, setBusy] = useState(false);
  const submitting = useRef(false);
  const pending = useRef<{ key: string; body: unknown } | undefined>(undefined);
  const fields = mapping.value?.data.fields ?? [];
  async function run() {
    if (submitting.current || !mapping.value || !model.value?.data.serving_available) return;
    const next: Record<string, string> = {};
    fields.forEach((f) => {
      const message = validation(f, inputs[f.field]);
      if (message) next[f.field] = message;
    });
    setErrors(next);
    setError(undefined);
    if (Object.keys(next).length) return;
    submitting.current = true;
    setBusy(true);
    pending.current ??= {
      key: crypto.randomUUID(),
      body: {
        schema_version: 'case-input-v1',
        model_version: model.value.evidence!.model_version,
        inputs: Object.fromEntries(
          fields.map((f) => [
            f.field,
            f.control === 'number' ? Number(inputs[f.field]) : inputs[f.field],
          ]),
        ),
      },
    };
    try {
      const response = await api.request('/analyses', analysisSchema, {
        body: pending.current.body,
        key: pending.current.key,
        private: true,
      });
      setResult(response.data);
      pending.current = undefined;
    } catch (e) {
      setError(e);
    } finally {
      submitting.current = false;
      setBusy(false);
    }
  }
  async function save() {
    if (!result || submitting.current) return;
    submitting.current = true;
    setBusy(true);
    setError(undefined);
    try {
      setResult(
        (
          await api.request('/analyses/' + result.prediction_id + '/save', analysisSchema, {
            body: {},
            private: true,
          })
        ).data,
      );
    } catch (e) {
      setError(e);
    } finally {
      submitting.current = false;
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading
        title="New Analysis"
        description="Enter case data for evaluation by the approved frozen model."
      />
      {!auth.token ? (
        <Access />
      ) : (
        <>
          <ResourceState
            loading={mapping.loading || model.loading}
            error={mapping.error ?? model.error}
            retry={() => {
              mapping.reload();
              model.reload();
            }}
          />
          {mapping.value && (
            <Panel title="Enter Case Data">
              <p>
                Do not enter names, account numbers, patient identifiers or other personally
                identifiable information.
              </p>
              <form
                noValidate
                onSubmit={(e) => {
                  e.preventDefault();
                  void run();
                }}
              >
                {Object.keys(errors).length > 0 && (
                  <p role="alert">Check the highlighted fields.</p>
                )}
                <fieldset disabled={busy}>
                  <legend>Encounter and prior-year observations</legend>
                  <div className="case-fields">
                    {fields.map((f) => (
                      <div className="form-field" key={f.field}>
                        <label htmlFor={f.field}>{f.label}</label>
                        {f.control === 'number' ? (
                          <input
                            id={f.field}
                            type="number"
                            step="1"
                            required
                            min={f.minimum!}
                            max={f.maximum!}
                            value={inputs[f.field] ?? ''}
                            aria-invalid={Boolean(errors[f.field])}
                            aria-describedby={
                              f.field + '-help ' + (errors[f.field] ? f.field + '-error' : '')
                            }
                            onChange={(e) => {
                              setInputs({ ...inputs, [f.field]: e.target.value });
                              pending.current = undefined;
                              setResult(undefined);
                            }}
                          />
                        ) : (
                          <select
                            id={f.field}
                            required
                            value={inputs[f.field] ?? ''}
                            aria-invalid={Boolean(errors[f.field])}
                            aria-describedby={
                              f.field + '-help ' + (errors[f.field] ? f.field + '-error' : '')
                            }
                            onChange={(e) => {
                              setInputs({ ...inputs, [f.field]: e.target.value });
                              pending.current = undefined;
                              setResult(undefined);
                            }}
                          >
                            <option value="">Select…</option>
                            {f.options.map((o) => (
                              <option key={o.value} value={o.value}>
                                {o.label}
                              </option>
                            ))}
                          </select>
                        )}
                        <small id={f.field + '-help'}>
                          {f.control === 'number' ? `${f.minimum}–${f.maximum} ${f.unit}. ` : ''}
                          {f.help}
                        </small>
                        {errors[f.field] && <span id={f.field + '-error'}>{errors[f.field]}</span>}
                      </div>
                    ))}
                  </div>
                </fieldset>
                <button
                  className="button primary"
                  disabled={busy || !model.value?.data.serving_available}
                >
                  {busy ? 'Running…' : pending.current ? 'Retry same analysis' : 'Run Analysis'}
                </button>{' '}
                <button
                  type="button"
                  className="button secondary"
                  disabled={busy}
                  onClick={() => {
                    setInputs({});
                    setErrors({});
                    setError(undefined);
                    setResult(undefined);
                    pending.current = undefined;
                  }}
                >
                  Reset Form
                </button>
              </form>
              <p className="small">
                For educational and research use. Not intended for real-world automated
                decision-making.
              </p>
              {Boolean(error) && <p role="alert">{errorCopy(error)}</p>}
              {pending.current && Boolean(error) && (
                <p>
                  Retry uses the original submission. A timeout can leave an already recorded
                  prediction.
                </p>
              )}
              {error instanceof ApiError && error.status === 409 && (
                <button
                  onClick={() => {
                    pending.current = undefined;
                    setError(undefined);
                    model.reload();
                  }}
                >
                  Refresh model context
                </button>
              )}
            </Panel>
          )}
          {result && (
            <Result
              result={result}
              busy={busy}
              onSave={() => void save()}
              onLoad={() => navigate('/new-analysis', { state: { inputs: result.inputs } })}
            />
          )}
        </>
      )}
    </>
  );
}

export function SavedAnalysis() {
  const { id } = useParams();
  const auth = useAuth();
  const api = useContext(ApiContext);
  const navigate = useNavigate();
  const record = useResource(
    auth.token ? '/analyses/' + encodeURIComponent(id ?? '') : undefined,
    analysisSchema,
    true,
  );
  const [error, setError] = useState<unknown>();
  const [busy, setBusy] = useState(false);
  async function save() {
    if (busy) return;
    setBusy(true);
    try {
      await api.request('/analyses/' + id + '/save', analysisSchema, { body: {}, private: true });
      record.reload();
    } catch (e) {
      setError(e);
    } finally {
      setBusy(false);
    }
  }
  return (
    <>
      <PageHeading
        title="Saved Analysis"
        description="Inspect the recorded inputs and immutable model output."
      />
      {!auth.token ? (
        <Access />
      ) : (
        <>
          <ResourceState
            loading={record.loading}
            error={record.error ?? error}
            retry={record.reload}
          />
          {record.value && (
            <Result
              result={record.value.data}
              busy={busy}
              onSave={() => void save()}
              onLoad={() =>
                navigate('/new-analysis', { state: { inputs: record.value!.data.inputs } })
              }
            />
          )}
        </>
      )}
    </>
  );
}
export function AnalysisHistory() {
  const auth = useAuth();
  const [cursor, setCursor] = useState('');
  const history = useResource(
    auth.token ? '/analyses' + (cursor ? '?cursor=' + encodeURIComponent(cursor) : '') : undefined,
    analysesSchema,
    true,
  );
  return (
    <>
      <PageHeading
        title="Analysis History"
        description="Saved analyses permitted by your current access scope."
      />
      {!auth.token ? (
        <Access />
      ) : (
        <>
          <ResourceState loading={history.loading} error={history.error} retry={history.reload} />
          <Panel title="Saved analyses">
            {history.value?.data.items.length === 0 && <p>No saved analyses.</p>}
            {history.value?.data.items.map((r) => (
              <p key={r.prediction_id}>
                <Link to={'/analyses/' + r.prediction_id}>Open analysis {r.prediction_id}</Link>
                <br />
                {r.created_at} · Model {r.model_version} · {r.category} ·{' '}
                {displayText(r.review_state)}
              </p>
            ))}
            {history.value?.data.next_cursor && (
              <button onClick={() => setCursor(history.value!.data.next_cursor!)}>Next page</button>
            )}
            {cursor && <button onClick={() => setCursor('')}>First page</button>}
          </Panel>
        </>
      )}
    </>
  );
}
