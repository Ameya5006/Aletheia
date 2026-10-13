import { z } from 'zod';
import { envelopeSchema, type Result } from './contracts';

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    public requestId?: string,
  ) {
    super(code.replaceAll('_', ' '));
  }
}
export function errorCopy(error: unknown): string {
  if (!(error instanceof ApiError)) return 'The request could not be completed. Please retry.';
  const messages: Record<number, string> = {
    0: 'The service could not be reached. No substitute results are shown.',
    401: 'Your session has expired. Sign in again.',
    403: 'Your account does not have access to this action.',
    404: 'This resource is absent or is outside your access scope.',
    409: 'The version, review revision or retry payload has changed. Refresh before continuing.',
    422: 'The API rejected this request. Check the required fields.',
    429: 'The request limit was reached. Wait before retrying.',
    503: 'The service is unavailable. A result has not been confirmed.',
    504: 'The request timed out. Retry the same submission to resolve its outcome.',
  };
  return messages[error.status] ?? 'The service returned an error. No result has been confirmed.';
}
export class ApiClient {
  constructor(
    private base = import.meta.env.VITE_API_BASE_URL || '/api/v1',
    private token: () => string | undefined = () => undefined,
    private expired: () => void = () => {},
    private transport: typeof fetch = (...args) => fetch(...args),
    private timeoutMs = 12000,
  ) {
    const url = new URL(base, window.location.origin);
    if (
      url.username ||
      url.password ||
      url.search ||
      url.hash ||
      !['http:', 'https:'].includes(url.protocol) ||
      (import.meta.env.PROD && url.origin !== window.location.origin && url.protocol !== 'https:')
    )
      throw new Error('Invalid API base URL');
    this.base = base.replace(/\/$/, '');
  }
  async request<T>(
    path: string,
    schema: z.ZodType<T>,
    options: { signal?: AbortSignal; body?: unknown; key?: string; private?: boolean } = {},
  ): Promise<Result<T>> {
    const controller = new AbortController();
    const cancel = () => controller.abort();
    options.signal?.addEventListener('abort', cancel, { once: true });
    if (options.signal?.aborted) cancel();
    const timer = setTimeout(cancel, this.timeoutMs);
    const requestId = crypto.randomUUID();
    try {
      const headers: Record<string, string> = {
        Accept: 'application/json',
        'X-Request-ID': requestId,
      };
      if (options.private) {
        const token = this.token();
        if (!token) throw new ApiError(401, 'sign_in_required', requestId);
        headers.Authorization = `Bearer ${token}`;
      }
      if (options.body !== undefined) headers['Content-Type'] = 'application/json';
      if (options.key) headers['Idempotency-Key'] = options.key;
      const response = await this.transport(this.base + path, {
        method: options.body === undefined ? 'GET' : 'POST',
        headers,
        body: options.body === undefined ? undefined : JSON.stringify(options.body),
        signal: controller.signal,
        credentials: 'omit',
        cache: 'no-store',
        redirect: 'error',
      });
      const raw: unknown = await response.json().catch(() => null);
      const failure = z
        .object({ request_id: z.string(), error: z.object({ code: z.string() }) })
        .safeParse(raw);
      if (!response.ok) {
        if (response.status === 401 && options.private) this.expired();
        throw new ApiError(
          response.status,
          failure.success ? failure.data.error.code : 'service_error',
          failure.success ? failure.data.request_id : requestId,
        );
      }
      const envelope = envelopeSchema.safeParse(raw);
      if (!envelope.success) throw new ApiError(502, 'response_contract_mismatch', requestId);
      const data = schema.safeParse(envelope.data.data);
      if (!data.success)
        throw new ApiError(502, 'response_contract_mismatch', envelope.data.request_id);
      if (!path.startsWith('/health/') && !envelope.data.evidence)
        throw new ApiError(502, 'missing_evidence_context', envelope.data.request_id);
      return {
        data: data.data,
        request_id: envelope.data.request_id,
        evidence: envelope.data.evidence,
      };
    } catch (error) {
      if (error instanceof ApiError) throw error;
      if (options.signal?.aborted) throw new DOMException('Cancelled', 'AbortError');
      throw new ApiError(
        controller.signal.aborted ? 504 : 0,
        controller.signal.aborted ? 'deadline_exceeded' : 'network_unavailable',
        requestId,
      );
    } finally {
      clearTimeout(timer);
      options.signal?.removeEventListener('abort', cancel);
    }
  }
}
