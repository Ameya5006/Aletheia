import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { afterEach, expect, it, vi } from 'vitest';
import { SessionProvider, useAuth } from '../src/auth/session';
import { envelope, jsonResponse } from './fixtures';

afterEach(() => vi.unstubAllGlobals());

function Probe({ token }: { token: string }) {
  const auth = useAuth();
  return (
    <>
      <button onClick={() => void auth.connectLocal?.(token)}>Connect</button>
      <output>{auth.roles.join(',')}</output>
    </>
  );
}

it('validates a provisioned token through protected history and keeps it in memory', async () => {
  vi.stubEnv('VITE_LOCAL_IDENTITY', 'false');
  vi.stubEnv('VITE_PROVISIONED_IDENTITY', 'true');
  const fetcher = vi.fn<typeof fetch>(async () =>
    jsonResponse(envelope({ items: [], next_cursor: null })),
  );
  vi.stubGlobal('fetch', fetcher);
  const payload = btoa(JSON.stringify({ roles: ['engineer', 'untrusted-role'] }));
  const token = `header.${payload}.signature`;
  render(
    <MemoryRouter>
      <SessionProvider>
        <Probe token={token} />
      </SessionProvider>
    </MemoryRouter>,
  );
  fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
  await waitFor(() => expect(screen.getByText('engineer')).toBeInTheDocument());
  expect(fetcher).toHaveBeenCalledOnce();
  expect(fetcher.mock.calls[0]?.[0]).toBe('/api/v1/analyses?limit=1');
  expect(fetcher.mock.calls[0]?.[1]?.headers).toMatchObject({ Authorization: `Bearer ${token}` });
  expect(sessionStorage.length).toBe(0);
});
