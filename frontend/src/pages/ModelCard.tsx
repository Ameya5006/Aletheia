import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Link, useParams } from 'react-router-dom';
import { useState } from 'react';
import { useResource } from '../api/context';
import { cardSchema, modelSchema, pageSchema, versionSchema } from '../api/contracts';
import { useAuth } from '../auth/session';
import { PageHeading } from '../components/Shell';
import {
  displayText,
  fieldLabel,
  Notice,
  Panel,
  Provenance,
  ResourceState,
} from '../components/ui';
const versionsPage = pageSchema(versionSchema);
export function ModelCard() {
  const card = useResource('/models/current/card', cardSchema);
  const model = useResource('/models/current', modelSchema);
  return (
    <>
      <PageHeading
        title="Model Card"
        description="Intended use, validation design and the boundaries of the published model."
      />
      <ResourceState
        loading={model.loading || card.loading}
        error={model.error ?? card.error}
        retry={() => {
          model.reload();
          card.reload();
        }}
      />
      {model.value && (
        <Panel title="Current release">
          <dl className="facts">
            <div>
              <dt>Model family / version</dt>
              <dd>
                {model.value.data.family} / {model.value.evidence?.model_version}
              </dd>
            </div>
            <div>
              <dt>Calibration</dt>
              <dd>{model.value.data.calibration}</dd>
            </div>
            <div>
              <dt>Approval status</dt>
              <dd>{model.value.data.approval_status}</dd>
            </div>
            <div>
              <dt>Serving available</dt>
              <dd>{model.value.data.serving_available ? 'Yes' : 'No'}</dd>
            </div>
            <div>
              <dt>Feature policy</dt>
              <dd>{model.value.data.feature_policy_version}</dd>
            </div>
          </dl>
          {!model.value.data.serving_available && (
            <Notice tone="warning">
              Serving is unavailable. The public metadata does not identify whether the cause is
              revocation or another readiness failure.
            </Notice>
          )}
        </Panel>
      )}
      {card.value && (
        <article className="model-document">
          <Notice>{displayText(card.value.data.limitations)}</Notice>
          <Markdown
            remarkPlugins={[remarkGfm]}
            skipHtml
            components={{
              a: ({ href, children }) => (
                <a
                  href={href?.startsWith('https://') ? href : undefined}
                  rel="noreferrer"
                  target={href?.startsWith('https://') ? '_blank' : undefined}
                >
                  {children}
                </a>
              ),
              table: ({ children }) => (
                <div
                  className="table-scroll"
                  tabIndex={0}
                  role="region"
                  aria-label="Model card table"
                >
                  <table>{children}</table>
                </div>
              ),
            }}
          >
            {displayText(card.value.data.content_markdown)}
          </Markdown>
          <p className="mono small">Published card SHA-256: {card.value.data.card_sha256}</p>
        </article>
      )}
      <Provenance evidence={card.value?.evidence} />
    </>
  );
}
export function ReleaseEvidence() {
  const auth = useAuth();
  const { version } = useParams();
  const [cursor, setCursor] = useState<string>();
  const allowed = auth.roles.includes('administrator');
  const list = useResource(
    allowed && !version
      ? '/admin/model-versions?limit=20' + (cursor ? '&cursor=' + encodeURIComponent(cursor) : '')
      : undefined,
    versionsPage,
    true,
  );
  const detail = useResource(
    allowed && version ? '/admin/model-versions/' + encodeURIComponent(version) : undefined,
    versionSchema,
    true,
  );
  return (
    <>
      <PageHeading
        title="Release evidence"
        description="Read-only administrator view of registry identities and release events."
      />
      {!allowed ? (
        <Notice tone="warning">Administrator permission is required.</Notice>
      ) : (
        <>
          <ResourceState
            loading={list.loading || detail.loading}
            error={list.error ?? detail.error}
            retry={() => {
              list.reload();
              detail.reload();
            }}
          />
          {list.value && (
            <Panel title="Registered model versions">
              <ul>
                {list.value.data.items.map((m) => (
                  <li key={m.id}>
                    <Link to={'/admin/models/' + m.version}>
                      {m.registry_name} · version {m.version}
                    </Link>
                  </li>
                ))}
              </ul>
              {list.value.data.items.length === 0 && <p>No registered models are visible.</p>}
              {list.value.data.next_cursor && (
                <button onClick={() => setCursor(list.value!.data.next_cursor!)}>
                  Older versions
                </button>
              )}
            </Panel>
          )}
          {detail.value && (
            <Panel title={'Model version ' + detail.value.data.version}>
              <dl className="facts">
                {Object.entries(detail.value.data)
                  .filter(([key]) => !['runtime', 'release_events'].includes(key))
                  .map(([key, v]) => (
                    <div key={key}>
                      <dt>{fieldLabel(key)}</dt>
                      <dd className="mono">{displayText(String(v))}</dd>
                    </div>
                  ))}
              </dl>
              <details>
                <summary>Recorded runtime</summary>
                <pre>{JSON.stringify(detail.value.data.runtime, null, 2)}</pre>
              </details>
              <h3>Release lifecycle events</h3>
              <ol className="timeline">
                {detail.value.data.release_events?.map((event) => (
                  <li key={event.id}>
                    <strong>{fieldLabel(event.action)}</strong>
                    <time>{event.created_at}</time>
                    <Link to={'/audit-history/' + event.audit_event_id}>Release audit event →</Link>
                  </li>
                ))}
              </ol>
              <Notice>
                Lifecycle is recorded by these backend events. Changes require the private operator
                workflow.
              </Notice>
            </Panel>
          )}
          <Provenance evidence={detail.value?.evidence ?? list.value?.evidence} />
        </>
      )}
    </>
  );
}
