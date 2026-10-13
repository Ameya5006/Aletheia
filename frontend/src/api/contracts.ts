import { z } from 'zod';

export const CASE_ID = 'synthetic-discharge-v1' as const;
export const SCHEMA = 'application-v1' as const;
const numeric = z.number().finite();
const probability = numeric.min(0).max(1);
const hash = z.string().regex(/^[0-9a-f]{64}$/);
const uuid = z.uuid();
const scalar = z.union([z.string(), numeric, z.boolean(), z.null()]);
export const evidenceSchema = z.object({
  domain: z.literal('healthcare'),
  model_version: z.string().regex(/^[1-9][0-9]*$/),
  model_sha256: hash,
  audit_protocol_sha256: hash,
  audit_results_sha256: hash,
  research_revision: z.string(),
  educational_only: z.literal(true),
  not_medical_advice: z.literal(true),
  source: z.enum(['precomputed_research', 'synthetic_inference']),
  limitations: z.string(),
});
export type Evidence = z.infer<typeof evidenceSchema>;
export function sameEvidence(left?: Evidence, right?: Evidence): boolean {
  return Boolean(
    left &&
    right &&
    [
      'model_version',
      'model_sha256',
      'audit_protocol_sha256',
      'audit_results_sha256',
      'research_revision',
    ].every((key) => left[key as keyof Evidence] === right[key as keyof Evidence]),
  );
}
export const envelopeSchema = z.object({
  schema_version: z.literal(SCHEMA),
  request_id: uuid,
  data: z.unknown(),
  evidence: evidenceSchema.optional(),
});
export type Result<T> = { data: T; request_id: string; evidence?: Evidence };
export const modelSchema = z.object({
  domain: z.literal('healthcare'),
  target: z.literal('readmitted_30d'),
  family: z.string(),
  calibration: z.string(),
  feature_policy_version: z.string(),
  threshold: probability,
  approval_status: z.enum(['approved', 'unavailable']),
  serving_available: z.boolean(),
});
export const healthSchema = z.object({ status: z.enum(['alive', 'ready', 'unready']) });
export const casesSchema = z.array(
  z.object({
    id: z.literal(CASE_ID),
    source: z.literal('synthetic'),
    features: z.record(z.string(), scalar),
  }),
);
const localFeature = z.object({
  field: z.string(),
  value: z.string(),
  contribution: numeric,
  direction: z.enum(['raises', 'lowers', 'neutral']),
});
export const localSchema = z.object({
  baseline: probability,
  probability,
  features: z.array(localFeature),
  method: z.string(),
  output: z.string(),
  limitations: z.string(),
  identity: z.object({ model_sha256: hash }).passthrough(),
});
export const globalSchema = z.object({
  features: z.array(
    z.object({
      field: z.string(),
      mean_absolute_contribution: numeric.min(0),
      repeat_min: numeric,
      repeat_max: numeric,
      repeat_values: z.array(numeric),
    }),
  ),
  baselines: z.array(probability),
  method: z.string(),
  output: z.string(),
  population: z.string(),
  sample_size_per_repeat: z.number().int(),
  seeds: z.array(z.number().int()),
  limitations: z.string(),
});
const summary = z.object({
  mean: numeric.nullable(),
  min: numeric.nullable(),
  max: numeric.nullable(),
  undefined: z.number().int(),
});
const stabilitySummary = z.object({
  absolute_rank_correlation: summary,
  normalized_l1: summary,
  top_k_overlap: summary,
});
export const stabilitySchema = z.object({
  all: stabilitySummary,
  same_class: stabilitySummary,
  crossed_class: stabilitySummary,
  comparisons: z.number().int(),
  boundary_crossings: z.number().int(),
  above_distance_reference: z.number().int(),
  below_overlap_reference: z.number().int(),
  unchanged_at_bound: z.number().int(),
  bounds: z.record(z.string(), z.tuple([numeric, numeric])),
  mean_absolute_probability_change: numeric,
  max_absolute_probability_change: numeric,
  population: z.string(),
  limitations: z.string(),
});
const metricMap = z.record(z.string(), numeric.nullable());
const uncertainty = z.object({
  interval: z.tuple([numeric, numeric]).nullable(),
  valid_replicates: z.number().int(),
  undefined_replicates: z.number().int(),
});
export const subgroupsSchema = z.array(
  z.object({
    attribute: z.string(),
    group: z.string(),
    counts: z.record(z.string(), z.union([z.number().int().min(0), z.literal('<20')])),
    status: z.enum(['supported', 'insufficient_support']),
    reason: z.string().nullable(),
    metrics: metricMap.nullable(),
    uncertainty: z.record(z.string(), uncertainty).nullable(),
  }),
);
export const feasibilitySchema = z.object({
  status: z.literal('no_feasible_scenario'),
  search_performed: z.literal(false),
  candidates: z.array(z.unknown()).length(0),
  worked_example: z.string(),
  assessment: z.object({
    status: z.literal('no_defensible_recourse'),
    reason: z.string(),
    mutable: z.array(z.string()),
    conditionally_mutable: z.array(z.string()),
    immutable: z.array(z.string()),
    excluded: z.array(z.string()),
    distance_cost: z.null(),
    distance_reason: z.string(),
    limitations: z.string(),
  }),
});
export const cardSchema = z.object({
  content_markdown: z.string(),
  card_sha256: hash,
  intended_use: z.string(),
  limitations: z.string(),
});
export const predictionSchema = z.object({
  prediction_id: uuid,
  case_id: z.literal(CASE_ID),
  input_sha256: hash,
  probability,
  threshold: probability,
  class_at_threshold: z.union([z.literal(0), z.literal(1)]),
  positive_class: z.literal(1),
  explanation_ref: uuid,
  event_id: uuid,
  created_at: z.string(),
});
export const predictionRequestSchema = z
  .object({
    schema_version: z.literal(SCHEMA),
    case_id: z.literal(CASE_ID),
    model_version: z.string().regex(/^[1-9][0-9]*$/),
  })
  .strict();
export const reviewRequestSchema = z
  .object({
    schema_version: z.literal(SCHEMA),
    decision: z.enum(['acknowledged', 'needs_investigation', 'dismissed_demo']),
    reason_code: z.enum(['evidence_reviewed', 'limitations_noted', 'identity_issue']),
    expected_revision: z.number().int().min(0),
  })
  .strict();
export const reviewSchema = z.object({
  review_id: uuid,
  prediction_id: uuid,
  revision: z.number().int().min(1),
  decision: reviewRequestSchema.shape.decision,
  reason_code: reviewRequestSchema.shape.reason_code,
  event_id: uuid,
  created_at: z.string(),
});
export const eventSchema = z.object({
  id: uuid,
  chain_id: z.string(),
  sequence: z.number().int(),
  request_id: uuid,
  event_type: z.string(),
  resource_id: uuid,
  payload: z.record(z.string(), z.unknown()),
  occurred_at: z.string(),
  prev_hash: hash,
  event_hash: hash,
  chain_version: z.literal('audit-chain-v1'),
});
export const versionSchema = z.object({
  id: uuid,
  registry_name: z.string(),
  version: z.string(),
  run_id: z.string(),
  model_sha256: hash,
  package_sha256: hash,
  release_sha256: hash,
  config_sha256: hash,
  selection_sha256: hash,
  split_sha256: hash,
  protocol_sha256: hash,
  results_sha256: hash,
  signature_version: z.string(),
  runtime: z.record(z.string(), z.unknown()),
  created_at: z.string(),
  release_events: z
    .array(
      z
        .object({
          id: uuid,
          action: z.enum(['approved', 'revoked', 'activated', 'rolled_back']),
          audit_event_id: uuid,
          created_at: z.string(),
        })
        .passthrough(),
    )
    .optional(),
});
export const pageSchema = <T extends z.ZodType>(item: T) =>
  z.object({ items: z.array(item), next_cursor: z.string().nullable() });
export type Model = z.infer<typeof modelSchema>;
export type LocalExplanation = z.infer<typeof localSchema>;
export type Prediction = z.infer<typeof predictionSchema>;
export type ReviewRequest = z.infer<typeof reviewRequestSchema>;
export type Review = z.infer<typeof reviewSchema>;
export type AuditEvent = z.infer<typeof eventSchema>;
