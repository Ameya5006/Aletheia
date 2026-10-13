import { render, screen, act, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { useContext } from 'react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { SessionProvider, useAuth, createManager } from '../src/auth/session';
import { ApiContext } from '../src/api/context';
import { z } from 'zod';
import { apiFailure } from './fixtures';
const mocks = vi.hoisted(() => ({
  settings: undefined as unknown,
  callback: vi.fn(),
  remove: vi.fn(async () => {}),
  redirect: vi.fn(async () => {}),
  expired: undefined as (() => void) | undefined,
}));
vi.mock('oidc-client-ts', () => ({
  UserManager: class {
    constructor(settings: unknown) {
      mocks.settings = settings;
    }
    events = {
      addAccessTokenExpired: (fn: () => void) => {
        mocks.expired = fn;
      },
      removeAccessTokenExpired: () => {
        mocks.expired = undefined;
      },
    };
    signinRedirect = mocks.redirect;
    signinRedirectCallback = mocks.callback;
    removeUser = mocks.remove;
  },
  WebStorageStateStore: class {
    constructor(public options: unknown) {}
  },
  InMemoryWebStorage: class {},
}));
function Controls() {
  const auth = useAuth();
  const api = useContext(ApiContext);
  return (
    <>
      <p>{auth.token ? 'authenticated' : 'viewer'}</p>
      <p>{auth.expired ? 'expired' : 'current'}</p>
      <p>{auth.roles.join(',')}</p>
      <button onClick={() => void auth.signIn()}>Sign in</button>
      <button onClick={auth.signOut}>Sign out</button>
      <button
        onClick={() => void api.request('/private', z.unknown(), { private: true }).catch(() => {})}
      >
        Private request
      </button>
    </>
  );
}
beforeEach(() => {
  vi.stubEnv('VITE_OIDC_AUTHORITY', 'https://identity.example.test');
  vi.stubEnv('VITE_OIDC_CLIENT_ID', 'frontend');
  window.history.replaceState({}, '', '/auth/callback');
  mocks.callback.mockResolvedValue({
    access_token: `header.${btoa(JSON.stringify({ roles: ['reviewer'] }))}.signature`,
    expired: false,
  });
});
describe('organization session lifecycle', () => {
  it('uses code flow and memory user storage with transient session PKCE state', () => {
    createManager();
    expect(mocks.settings).toMatchObject({
      response_type: 'code',
      automaticSilentRenew: false,
      userStore: { options: { store: {} } },
      stateStore: { options: { store: window.sessionStorage } },
    });
    expect(window.localStorage.length).toBe(0);
  });
  it('completes callback and clears session on sign-out', async () => {
    const user = userEvent.setup();
    render(
      <MemoryRouter>
        <SessionProvider>
          <Controls />
        </SessionProvider>
      </MemoryRouter>,
    );
    await screen.findByText('authenticated');
    expect(screen.getByText('reviewer')).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Sign out' }));
    expect(screen.getByText('viewer')).toBeVisible();
    expect(mocks.remove).toHaveBeenCalled();
  });
  it('expires session on provider expiry events', async () => {
    render(
      <MemoryRouter>
        <SessionProvider>
          <Controls />
        </SessionProvider>
      </MemoryRouter>,
    );
    await screen.findByText('authenticated');
    act(() => mocks.expired?.());
    expect(screen.getByText('expired')).toBeVisible();
    expect(screen.getByText('viewer')).toBeVisible();
  });
  it('expires session when the authoritative API rejects the token', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(apiFailure(401, 'invalid_token')));
    render(
      <MemoryRouter>
        <SessionProvider>
          <Controls />
        </SessionProvider>
      </MemoryRouter>,
    );
    await screen.findByText('authenticated');
    await userEvent.setup().click(screen.getByRole('button', { name: 'Private request' }));
    await screen.findByText('expired');
    expect(screen.getByText('viewer')).toBeVisible();
    vi.unstubAllGlobals();
  });
  it('handles a rejected callback without leaving URL credentials', async () => {
    mocks.callback.mockRejectedValueOnce(new Error('provider rejected'));
    render(
      <MemoryRouter>
        <SessionProvider>
          <Controls />
        </SessionProvider>
      </MemoryRouter>,
    );
    await screen.findByText('expired');
    expect(window.location.search).toBe('');
  });
  it('starts organization SSO only through the configured manager', async () => {
    window.history.replaceState({}, '', '/sign-in');
    render(
      <MemoryRouter>
        <SessionProvider>
          <Controls />
        </SessionProvider>
      </MemoryRouter>,
    );
    await userEvent.setup().click(screen.getByRole('button', { name: 'Sign in' }));
    await waitFor(() => expect(mocks.redirect).toHaveBeenCalled());
  });
});
