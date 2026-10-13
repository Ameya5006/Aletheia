import { describe, it, expect, vi } from 'vitest';
import { z } from 'zod';
import { ApiClient, ApiError, errorCopy } from '../src/api/client';
import { modelSchema } from '../src/api/contracts';
import { publicResponses, jsonResponse, apiFailure, envelope } from './fixtures';
describe('HTTP boundary', () => {
  it('validates the actual public FastAPI response and correlates requests', async () => {
    const transport = vi
      .fn<typeof fetch>()
      .mockResolvedValue(jsonResponse(publicResponses['/models/current']));
    const api = new ApiClient('/api/v1', undefined, undefined, transport);
    const result = await api.request('/models/current', modelSchema);
    expect(result.data.family).toBe('histogram');
    expect(result.evidence?.source).toBe('precomputed_research');
    const options = transport.mock.calls[0]?.[1];
    expect(options?.credentials).toBe('omit');
    expect(options?.cache).toBe('no-store');
    expect((options?.headers as Record<string, string>)['X-Request-ID']).toMatch(/^[0-9a-f-]{36}$/);
  });
  it.each([401, 403, 404, 409, 422, 429, 500, 503, 504])(
    'normalizes %i without substitute data',
    async (status) => {
      const expired = vi.fn();
      const api = new ApiClient(
        '/api/v1',
        () => 'private-token',
        expired,
        vi.fn<typeof fetch>().mockResolvedValue(apiFailure(status)),
      );
      await expect(
        api.request('/models/current', modelSchema, { private: true }),
      ).rejects.toMatchObject({ status });
      expect(expired).toHaveBeenCalledTimes(status === 401 ? 1 : 0);
      expect(errorCopy(new ApiError(status, 'test'))).toBeTruthy();
    },
  );
  it('requires authentication before a private transport call', async () => {
    const transport = vi.fn<typeof fetch>();
    const api = new ApiClient('/api/v1', undefined, undefined, transport);
    await expect(
      api.request('/predictions/id', z.unknown(), { private: true }),
    ).rejects.toMatchObject({ status: 401 });
    expect(transport).not.toHaveBeenCalled();
  });
  it('fails closed for schema or evidence drift', async () => {
    const transport = vi
      .fn<typeof fetch>()
      .mockResolvedValueOnce(jsonResponse(envelope({ family: 'fabricated' })))
      .mockResolvedValueOnce(
        jsonResponse({
          schema_version: 'application-v1',
          request_id: '00000000-0000-4000-8000-000000000001',
          data: {},
        }),
      );
    const api = new ApiClient('/api/v1', undefined, undefined, transport);
    await expect(api.request('/models/current', modelSchema)).rejects.toMatchObject({
      status: 502,
    });
    await expect(api.request('/demo/cases', z.unknown())).rejects.toMatchObject({
      code: 'missing_evidence_context',
    });
  });
  it('never falls back after a network error', async () => {
    const api = new ApiClient(
      '/api/v1',
      undefined,
      undefined,
      vi.fn<typeof fetch>().mockRejectedValue(new TypeError('offline')),
    );
    await expect(api.request('/models/current', modelSchema)).rejects.toMatchObject({ status: 0 });
  });
  it('distinguishes a timeout from caller cancellation', async () => {
    const transport: typeof fetch = (_url, options) =>
      new Promise((_resolve, reject) => {
        options?.signal?.addEventListener('abort', () =>
          reject(new DOMException('Aborted', 'AbortError')),
        );
        if (options?.signal?.aborted) reject(new DOMException('Aborted', 'AbortError'));
      });
    const api = new ApiClient('/api/v1', undefined, undefined, transport, 10);
    await expect(api.request('/models/current', modelSchema)).rejects.toMatchObject({
      status: 504,
    });
    const controller = new AbortController();
    const pending = api.request('/models/current', modelSchema, { signal: controller.signal });
    controller.abort();
    await expect(pending).rejects.toMatchObject({ name: 'AbortError' });
  });
  it('uses the supplied idempotency identity and body', async () => {
    const transport = vi.fn<typeof fetch>().mockResolvedValue(jsonResponse(envelope({ ok: true })));
    const api = new ApiClient('/api/v1', () => 'access', undefined, transport);
    await api.request('/predictions', z.object({ ok: z.boolean() }), {
      body: { case_id: 'synthetic-discharge-v1' },
      key: 'key',
      private: true,
    });
    expect(transport.mock.calls[0]?.[1]).toMatchObject({
      method: 'POST',
      body: '{"case_id":"synthetic-discharge-v1"}',
      headers: { Authorization: 'Bearer access', 'Idempotency-Key': 'key' },
    });
  });
});
