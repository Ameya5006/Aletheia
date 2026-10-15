import { z } from 'zod';
import { evidenceSchema, stabilitySchema, reviewSchema } from './contracts';

const number = z.number().finite();
const hash = z.string().regex(/^[0-9a-f]{64}$/);
export const inputFieldsSchema = z.object({
  schema_version: z.literal('case-input-v1'),
  fields: z.array(
    z.object({
      field: z.string(),
      label: z.string(),
      required: z.literal(true),
      control: z.enum(['number', 'select']),
      unit: z.string(),
      help: z.string(),
      minimum: number.nullable(),
      maximum: number.nullable(),
      conversion: z.string(),
      options: z.array(z.object({ value: z.string(), label: z.string() })),
    }),
  ),
});
export type InputField = z.infer<typeof inputFieldsSchema>['fields'][number];
export const analysisSchema = z.object({
  schema_version: z.literal('case-result-v1'),
  inputs: z.record(z.string(), z.string()),
  probability: number.min(0).max(1),
  threshold: z.literal(0.5),
  class_at_threshold: z.union([z.literal(0), z.literal(1)]),
  positive_class: z.literal(1),
  category: z.string(),
  model_version: z.string(),
  model_sha256: hash,
  release_sha256: hash,
  evidence_sha256: hash,
  evidence: evidenceSchema,
  prediction_id: z.uuid(),
  event_id: z.uuid(),
  input_sha256: hash,
  created_at: z.string(),
  saved: z.boolean(),
  save_event_id: z.uuid().nullable(),
  review_state: z.string(),
  review_history: z.array(reviewSchema),
  limitations: z.string(),
  explanation: z.object({
    baseline: number,
    probability: number,
    method: z.string(),
    reference_scope: z.string(),
    reference_inputs: z.record(z.string(), z.string()),
    limitations: z.string(),
    features: z.array(
      z.object({
        field: z.string(),
        label: z.string(),
        value: z.string(),
        contribution: number,
        direction: z.enum(['raises', 'lowers', 'zero']),
      }),
    ),
  }),
  stability: z.object({
    scope: z.literal('model_level'),
    per_case_score: z.null(),
    evidence: stabilitySchema,
  }),
});
export type Analysis = z.infer<typeof analysisSchema>;
export const analysesSchema = z.object({
  items: z.array(analysisSchema),
  next_cursor: z.string().nullable(),
});
