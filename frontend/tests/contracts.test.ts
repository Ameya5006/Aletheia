import { describe, it, expect } from 'vitest';
import { User } from 'oidc-client-ts';
import schema from '../contracts/openapi.json';
import {
  casesSchema,
  cardSchema,
  globalSchema,
  localSchema,
  modelSchema,
  healthSchema,
  stabilitySchema,
  subgroupsSchema,
  feasibilitySchema,
  predictionRequestSchema,
  reviewRequestSchema,
  sameEvidence,
} from '../src/api/contracts';
import { sessionFromUser, createManager } from '../src/auth/session';
import { publicResponses, evidence } from './fixtures';
const validators = {
  '/demo/cases': casesSchema,
  '/models/current': modelSchema,
  '/models/current/card': cardSchema,
  '/health/live': healthSchema,
  '/health/ready': healthSchema,
  '/explanations/global': globalSchema,
  '/explanations/local/synthetic-discharge-v1': localSchema,
  '/audits/stability': stabilitySchema,
  '/audits/subgroups': subgroupsSchema,
  '/counterfactuals/feasibility': feasibilitySchema,
};
describe('real FastAPI contract', () => {
  it.each(Object.entries(validators))('maps %s from real Stage 1 responses', (path, validator) => {
    const raw = publicResponses[path] as { data: unknown };
    expect(validator.safeParse(raw.data).success).toBe(true);
    expect(schema.paths).toHaveProperty('/api/v1' + path);
  });
  it('preserves enums and strict synthetic-only request boundaries', () => {
    const requests = schema.components.schemas;
    expect(requests.PredictionRequest.additionalProperties).toBe(false);
    expect(requests.PredictionRequest.properties.case_id.const).toBe('synthetic-discharge-v1');
    expect(requests.ReviewRequest.properties.decision.enum).toEqual(
      reviewRequestSchema.shape.decision.options,
    );
    expect(requests.ReviewRequest.properties.reason_code.enum).toEqual(
      reviewRequestSchema.shape.reason_code.options,
    );
    expect(
      predictionRequestSchema.safeParse({
        schema_version: 'application-v1',
        case_id: 'patient',
        model_version: '1',
      }).success,
    ).toBe(false);
    expect(
      reviewRequestSchema.safeParse({
        schema_version: 'application-v1',
        decision: 'acknowledged',
        reason_code: 'evidence_reviewed',
        expected_revision: 0,
        comment: 'patient',
      }).success,
    ).toBe(false);
  });
  it('requires all release and audit identity fields to agree', () => {
    expect(sameEvidence(evidence, { ...evidence })).toBe(true);
    expect(sameEvidence(evidence, { ...evidence, audit_results_sha256: 'a'.repeat(64) })).toBe(
      false,
    );
    expect(sameEvidence(undefined, evidence)).toBe(false);
  });
});
describe('OIDC UI session hints', () => {
  const user = (roles: unknown, expired = false) =>
    new User({
      access_token: `header.${btoa(JSON.stringify({ roles }))}.signature`,
      token_type: 'Bearer',
      profile: {
        sub: 'synthetic',
        iss: 'https://identity.example.test',
        aud: 'frontend',
        exp: 9999999999,
        iat: 1,
      },
      expires_at: expired ? 1 : 9999999999,
    });
  it('reads access-token roles and never grants unknown or inherited permissions', () => {
    expect(sessionFromUser(user(['administrator', 'unknown'])).roles).toEqual(['administrator']);
    expect(sessionFromUser(user('reviewer')).roles).toEqual([]);
    expect(sessionFromUser(user(['reviewer'], true))).toEqual({ roles: [], expired: true });
  });
  it('keeps organization SSO unavailable when unconfigured', () => {
    expect(createManager()).toBeUndefined();
  });
});
