import { useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useResource } from '../api/context';
import { eventSchema, pageSchema } from '../api/contracts';
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
const eventPage = pageSchema(eventSchema);
export function AuditTrail() {
  const auth = useAuth();
  const { eventId } = useParams();
  const [cursor, setCursor] = useState<string>();
  const [filter, setFilter] = useState('');
  const events = useResource(
    auth.token && !eventId
      ? '/audit-events?limit=20' + (cursor ? '&cursor=' + encodeURIComponent(cursor) : '')
      : undefined,
    eventPage,
    true,
  );
  const detail = useResource(
    auth.token && eventId ? '/audit-events/' + encodeURIComponent(eventId) : undefined,
    eventSchema,
    true,
  );
  const resource = eventId ? detail : events;
  return (
    <>
      <PageHeading
        title="Audit Trail"
        description="Backend-committed activity within your authorized resource scope."
      />
      {!auth.token ? (
        <Notice>
          <Link to="/sign-in">Sign in to inspect audit events.</Link>
        </Notice>
      ) : (
        <>
          <Notice>
            Hash links are returned by the backend. This role-filtered page cannot verify the
            complete chain, and the API publishes no verification verdict or actor-role snapshot.
          </Notice>
          <ResourceState
            loading={resource.loading}
            error={resource.error}
            retry={resource.reload}
          />
          {events.value && (
            <Panel
              title="Committed events"
              aside={<span className="small muted">20 events per page</span>}
            >
              <label className="form-field">
                Filter loaded page by event type
                <select value={filter} onChange={(e) => setFilter(e.target.value)}>
                  <option value="">All loaded event types</option>
                  {[...new Set(events.value.data.items.map((e) => e.event_type))].map((type) => (
                    <option key={type} value={type}>
                      {fieldLabel(type)}
                    </option>
                  ))}
                </select>
              </label>
              <div className="table-scroll">
                <table>
                  <caption>
                    Authorized events, newest first. Filtering applies to this loaded page only.
                  </caption>
                  <thead>
                    <tr>
                      <th>Sequence</th>
                      <th>Event</th>
                      <th>Timestamp</th>
                      <th>Resource</th>
                      <th>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {events.value.data.items
                      .filter((e) => !filter || e.event_type === filter)
                      .map((e) => (
                        <tr key={e.id}>
                          <td>{e.sequence}</td>
                          <th scope="row">{fieldLabel(e.event_type)}</th>
                          <td>
                            <time>{e.occurred_at}</time>
                          </td>
                          <td className="mono">{e.resource_id}</td>
                          <td>
                            <Link to={'/audit-history/' + e.id}>Inspect event</Link>
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
              {events.value.data.items.filter((e) => !filter || e.event_type === filter).length ===
                0 && <p>No events match this loaded page.</p>}
              <div className="actions">
                {cursor && (
                  <button className="button secondary" onClick={() => setCursor(undefined)}>
                    Newest page
                  </button>
                )}
                {events.value.data.next_cursor && (
                  <button
                    className="button secondary"
                    onClick={() => setCursor(events.value!.data.next_cursor!)}
                  >
                    Older events →
                  </button>
                )}
              </div>
            </Panel>
          )}
          {detail.value && (
            <Panel title={fieldLabel(detail.value.data.event_type)}>
              <Link to="/audit-history">← Back to events</Link>
              <dl className="facts">
                {Object.entries(detail.value.data)
                  .filter(([key]) => key !== 'payload')
                  .map(([key, v]) => (
                    <div key={key}>
                      <dt>{fieldLabel(key)}</dt>
                      <dd className="mono">{String(v)}</dd>
                    </div>
                  ))}
                <div>
                  <dt>Actor role</dt>
                  <dd>Not published</dd>
                </div>
                <div>
                  <dt>Integrity verdict</dt>
                  <dd>Not published</dd>
                </div>
              </dl>
              <details open>
                <summary>Readable event payload (presentation labels)</summary>
                <pre>{displayText(JSON.stringify(detail.value.data.payload, null, 2))}</pre>
              </details>
            </Panel>
          )}
          <Provenance evidence={resource.value?.evidence} />
        </>
      )}
    </>
  );
}
