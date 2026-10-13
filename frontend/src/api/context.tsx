import { createContext, useContext, useEffect, useState } from 'react';
import type { z } from 'zod';
import { ApiClient } from './client';
import type { Result } from './contracts';
export const ApiContext = createContext(new ApiClient());
export function useResource<T>(
  path: string | undefined,
  schema: z.ZodType<T>,
  privateRequest = false,
) {
  const api = useContext(ApiContext);
  const [value, setValue] = useState<Result<T>>();
  const [error, setError] = useState<unknown>();
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    const controller = new AbortController();
    setValue(undefined);
    setError(undefined);
    setLoading(Boolean(path));
    if (path)
      void api
        .request(path, schema, { signal: controller.signal, private: privateRequest })
        .then((result) => {
          if (!controller.signal.aborted) setValue(result);
        })
        .catch((failure: unknown) => {
          if (!controller.signal.aborted) setError(failure);
        })
        .finally(() => {
          if (!controller.signal.aborted) setLoading(false);
        });
    return () => controller.abort();
  }, [api, path, schema, privateRequest, attempt]);
  return { value, error, loading, reload: () => setAttempt((n) => n + 1) };
}
