import { Link, Navigate, useParams } from 'react-router-dom';
import { useResource } from '../api/context';
import { predictionSchema } from '../api/contracts';
import { useAuth } from '../auth/session';
import { PageHeading } from '../components/Shell';
import { Panel, Probability, Provenance, ResourceState } from '../components/ui';
export function CaseAnalysis() {
  const { id } = useParams();
  const auth = useAuth();
  const record = useResource(
    auth.token && id ? '/predictions/' + encodeURIComponent(id) : undefined,
    predictionSchema,
    true,
  );
  const p = record.value;
  if (!id) return <Navigate to="/new-analysis" replace />;
  if (p?.data.case_id === 'entered-case-v1')
    return <Navigate to={'/analyses/' + encodeURIComponent(id)} replace />;
  return (
    <>
      <PageHeading
        title="Case Analysis"
        description="Inspect an authorized archived prediction and its recorded evidence."
      />
      {!auth.token ? (
        <p>
          An authorized provisioned identity is required.{' '}
          <Link to="/local-session">Connect provisioned identity</Link>.
        </p>
      ) : (
        <ResourceState loading={record.loading} error={record.error} retry={record.reload} />
      )}
      {auth.token && p && (
        <Panel title="Persisted prediction">
          <p>
            Archived reference prediction. Enter independent case data through{' '}
            <Link to="/new-analysis">New Analysis</Link>.
          </p>
          <Probability probability={p.data.probability} threshold={p.data.threshold} />
          <dl className="facts">
            <div>
              <dt>Prediction ID</dt>
              <dd className="mono">{p.data.prediction_id}</dd>
            </div>
            <div>
              <dt>Prediction timestamp</dt>
              <dd>
                <time>{p.data.created_at}</time>
              </dd>
            </div>
            <div>
              <dt>Explanation reference</dt>
              <dd className="mono">{p.data.explanation_ref}</dd>
            </div>
          </dl>
          <p>
            <Link to="/evidence/local">Inspect published reference explanation</Link>
          </p>
          <p>
            <Link to={'/predictions/' + p.data.prediction_id + '/review'}>
              Review this prediction
            </Link>
          </p>
          <Link to={'/audit-history/' + p.data.event_id}>Prediction audit event</Link>
        </Panel>
      )}
      <Provenance evidence={auth.token ? p?.evidence : undefined} />
    </>
  );
}
