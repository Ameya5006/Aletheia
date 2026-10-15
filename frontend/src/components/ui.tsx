import type { ReactNode } from 'react';
import { ApiError, errorCopy } from '../api/client';
import type { Evidence } from '../api/contracts';
// Presentation labels only: never mutate stored codes, response objects or hashes.
export const displayText = (text: string) =>
  text
    .replaceAll('synthetic-discharge-v1', 'Published reference case')
    .replaceAll('synthetic-v1', 'Reference input schema v1')
    .replaceAll('synthetic_inference', 'Reference inference')
    .replaceAll('dismissed_demo', 'dismissed')
    .replace(/fixed synthetic/gi, 'published reference')
    .replace(/\bsynthetic\b/gi, 'constructed')
    .replace(/\bdemonstration\b/gi, 'research workflow')
    .replace(/\bdemo\b/gi, 'reference');
export const fieldLabel = (field: string) => displayText(field).replaceAll('_', ' ');
export const number = (value: number | null | undefined, digits = 4) =>
  value == null ? 'Not available' : value.toFixed(digits);
export const percent = (value: number) => `${(value * 100).toFixed(2)}%`;
export function Panel({
  title,
  children,
  aside,
}: {
  title: string;
  children: ReactNode;
  aside?: ReactNode;
}) {
  return (
    <section className="panel">
      <header className="panel-heading">
        <h2>{title}</h2>
        {aside}
      </header>
      <div className="panel-body">{children}</div>
    </section>
  );
}
export function Notice({
  children,
  tone = 'neutral',
}: {
  children: ReactNode;
  tone?: 'neutral' | 'warning' | 'success';
}) {
  return <div className={`notice ${tone}`}>{children}</div>;
}
export function Status({ children }: { children: ReactNode }) {
  return <span className="chip">{children}</span>;
}
export function Metric({
  label,
  value,
  caption,
}: {
  label: string;
  value: ReactNode;
  caption?: ReactNode;
}) {
  return (
    <div className="metric">
      <span className="muted">{label}</span>
      <div className="metric-value">{value}</div>
      <small>{caption}</small>
    </div>
  );
}
export function ResourceState({
  loading,
  error,
  retry,
  empty = false,
}: {
  loading: boolean;
  error: unknown;
  retry: () => void;
  empty?: boolean;
}) {
  if (loading)
    return (
      <div role="status" className="loading">
        Loading evidence…
        <div className="skeleton" />
      </div>
    );
  if (error)
    return (
      <div role="alert" className="notice warning">
        <p>{errorCopy(error)}</p>
        {error instanceof ApiError && (
          <p className="mono small">
            {error.code} · Request {error.requestId ?? 'unavailable'}
          </p>
        )}
        <button className="button secondary" onClick={retry}>
          Retry request
        </button>
      </div>
    );
  if (empty) return <Notice>No evidence has been published for this view.</Notice>;
  return null;
}
export function Provenance({ evidence }: { evidence?: Evidence }) {
  if (!evidence) return null;
  return (
    <details className="provenance">
      <summary>Evidence provenance · model {evidence.model_version}</summary>
      <dl className="facts">
        <div>
          <dt>Source</dt>
          <dd>{fieldLabel(evidence.source)}</dd>
        </div>
        <div>
          <dt>Model SHA-256</dt>
          <dd className="mono">{evidence.model_sha256}</dd>
        </div>
        <div>
          <dt>Audit results SHA-256</dt>
          <dd className="mono">{evidence.audit_results_sha256}</dd>
        </div>
        <div>
          <dt>Audit protocol SHA-256</dt>
          <dd className="mono">{evidence.audit_protocol_sha256}</dd>
        </div>
        <div>
          <dt>Research revision</dt>
          <dd className="mono">{evidence.research_revision}</dd>
        </div>
      </dl>
      <p>{displayText(evidence.limitations)}</p>
    </details>
  );
}
export function Probability({
  probability,
  threshold,
}: {
  probability: number;
  threshold?: number;
}) {
  return (
    <div className="probability-panel">
      <div className="muted">30-day readmission probability</div>
      <div className="probability">
        {(probability * 100).toFixed(2)}
        <span>%</span>
      </div>
      {threshold !== undefined && (
        <>
          <div className="risk-track" aria-hidden="true">
            <div className="risk-fill" style={{ width: percent(probability) }} />
            <span className="threshold" style={{ left: percent(threshold) }} />
          </div>
          <p className="small">
            Configured threshold {percent(threshold)} ·{' '}
            {probability >= threshold ? 'At or above' : 'Below'} threshold
          </p>
        </>
      )}
      <p className="small muted">A calibrated model estimate, not a diagnosis.</p>
    </div>
  );
}
