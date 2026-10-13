// Real public FastAPI responses are generated read-only before tests. Private
// response fixtures exist only at the frontend HTTP boundary, never in src/.
import samples from './real-api-responses.json' with { type: 'json' };
import type { Evidence } from '../src/api/contracts';
export const publicResponses: Record<string, unknown> = samples;
export const requestId = '00000000-0000-4000-8000-000000000001';
export const predictionId = '00000000-0000-4000-8000-000000000002';
export const eventId = '00000000-0000-4000-8000-000000000003';
export const reviewId = '00000000-0000-4000-8000-000000000004';
export const evidence = samples['/models/current'].evidence as Evidence;
export const envelope = (data: unknown, source: Evidence['source'] = 'precomputed_research') => ({
  schema_version: 'application-v1',
  request_id: requestId,
  data,
  evidence: { ...evidence, source },
});
export const prediction = {
  prediction_id: predictionId,
  case_id: 'synthetic-discharge-v1',
  input_sha256: 'a'.repeat(64),
  probability: samples['/explanations/local/synthetic-discharge-v1'].data.probability,
  threshold: 0.5,
  class_at_threshold: 0,
  positive_class: 1,
  explanation_ref: reviewId,
  event_id: eventId,
  created_at: '2026-10-13T00:00:00Z',
};
export const review = {
  review_id: reviewId,
  prediction_id: predictionId,
  revision: 1,
  decision: 'acknowledged',
  reason_code: 'evidence_reviewed',
  event_id: eventId,
  created_at: '2026-10-13T00:00:00Z',
};
export const event = {
  id: eventId,
  chain_id: 'application',
  sequence: 5,
  request_id: requestId,
  event_type: 'prediction_created',
  resource_id: predictionId,
  payload: { case_id: 'synthetic-discharge-v1' },
  occurred_at: '2026-10-13T00:00:00Z',
  prev_hash: 'b'.repeat(64),
  event_hash: 'c'.repeat(64),
  chain_version: 'audit-chain-v1',
};
export const apiFailure = (status: number, code = 'service_unready') =>
  new Response(
    JSON.stringify({
      schema_version: 'application-v1',
      request_id: requestId,
      error: { code, message: code },
    }),
    { status, headers: { 'Content-Type': 'application/json' } },
  );
export const jsonResponse = (data: unknown, status = 200) =>
  new Response(JSON.stringify(data), { status, headers: { 'Content-Type': 'application/json' } });
