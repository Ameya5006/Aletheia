import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { UserManager, WebStorageStateStore, InMemoryWebStorage, type User } from 'oidc-client-ts';
import { useNavigate } from 'react-router-dom';
import { ApiContext } from '../api/context';
import { ApiClient } from '../api/client';
import { z } from 'zod';

export const ROLE_LABELS: Record<string, string> = {
  engineer: 'Model-Risk Auditor (engineer)',
  reviewer: 'Clinical Reviewer',
  administrator: 'Administrator',
};
export type Session = { token?: string; roles: string[]; expired: boolean };
type Auth = Session & {
  configured: boolean;
  signIn: () => Promise<void>;
  signOut: () => void;
  localAvailable?: boolean;
  connectLocal?: (token: string) => Promise<void>;
};
export const AuthContext = createContext<Auth>({
  roles: [],
  expired: false,
  configured: false,
  signIn: async () => {},
  signOut: () => {},
});
export const useAuth = () => useContext(AuthContext);
export function createManager(): UserManager | undefined {
  const authority = import.meta.env.VITE_OIDC_AUTHORITY;
  const clientId = import.meta.env.VITE_OIDC_CLIENT_ID;
  if (!authority || !clientId) return;
  if (new URL(authority).protocol !== 'https:')
    throw new Error('An HTTPS OIDC authority is required');
  return new UserManager({
    authority,
    client_id: clientId,
    redirect_uri: window.location.origin + '/auth/callback',
    post_logout_redirect_uri: window.location.origin + '/',
    response_type: 'code',
    scope: import.meta.env.VITE_OIDC_SCOPE || 'openid profile',
    extraQueryParams: { audience: import.meta.env.VITE_OIDC_AUDIENCE || 'aletheia-api' },
    userStore: new WebStorageStateStore({ store: new InMemoryWebStorage() }),
    stateStore: new WebStorageStateStore({ store: window.sessionStorage }),
    automaticSilentRenew: false,
    loadUserInfo: true,
    monitorSession: false,
  });
}
export function sessionFromUser(user: User): Session {
  // Claims arrive through the configured provider's token/userinfo flow. They are UI
  // hints only; the API independently validates access JWT and local entitlements.
  let claims: unknown;
  try {
    const segment = user.access_token.split('.')[1];
    if (segment)
      claims = (
        JSON.parse(atob(segment.replaceAll('-', '+').replaceAll('_', '/'))) as { roles?: unknown }
      ).roles;
  } catch {
    /* Unknown claims hide privileged controls; API remains authoritative. */
  }
  if (user.expired) return { roles: [], expired: true };
  return {
    token: user.access_token,
    roles: Array.isArray(claims)
      ? claims.filter((v): v is string => typeof v === 'string' && v in ROLE_LABELS)
      : [],
    expired: false,
  };
}
function provisionedRoles(token: string): string[] {
  try {
    const segment = token.split('.')[1];
    const claims: unknown = segment
      ? (JSON.parse(atob(segment.replaceAll('-', '+').replaceAll('_', '/'))) as unknown)
      : null;
    const roles = claims && typeof claims === 'object' && 'roles' in claims ? claims.roles : null;
    return Array.isArray(roles)
      ? roles.filter((role): role is string => typeof role === 'string' && role in ROLE_LABELS)
      : [];
  } catch {
    return [];
  }
}
export function SessionProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [manager] = useState(createManager);
  const [session, setSession] = useState<Session>({ roles: [], expired: false });
  const expire = () => {
    setSession({ roles: [], expired: true });
    void manager?.removeUser();
  };
  useEffect(() => {
    if (!manager) return;
    const expired = () => {
      setSession({ roles: [], expired: true });
      void manager.removeUser();
    };
    manager.events.addAccessTokenExpired(expired);
    if (window.location.pathname === '/auth/callback') {
      void manager
        .signinRedirectCallback()
        .then((user) => {
          setSession(sessionFromUser(user));
          window.history.replaceState({}, '', '/');
          navigate('/', { replace: true });
        })
        .catch(() => {
          window.history.replaceState({}, '', '/sign-in');
          setSession({ roles: [], expired: true });
          navigate('/sign-in', { replace: true });
        });
    }
    return () => manager.events.removeAccessTokenExpired(expired);
  }, [manager, navigate]);
  const api = useMemo(() => new ApiClient(undefined, () => session.token, expire), [session.token]);
  const auth: Auth = {
    ...session,
    configured: Boolean(manager),
    localAvailable:
      import.meta.env.VITE_LOCAL_IDENTITY === 'true' ||
      import.meta.env.VITE_PROVISIONED_IDENTITY === 'true',
    connectLocal: async (token) => {
      const local = import.meta.env.VITE_LOCAL_IDENTITY === 'true';
      if (!local && import.meta.env.VITE_PROVISIONED_IDENTITY !== 'true')
        throw new Error('Provisioned identity unavailable');
      const localApi = new ApiClient(undefined, () => token);
      if (local) {
        const result = await localApi.request(
          '/session',
          z.object({ roles: z.array(z.string()) }),
          {
            private: true,
          },
        );
        setSession({ token, roles: result.data.roles, expired: false });
      } else {
        await localApi.request(
          '/analyses?limit=1',
          z.object({ items: z.array(z.unknown()), next_cursor: z.string().nullable() }),
          { private: true },
        );
        // These are display hints; the API checks signed claims and DB entitlements.
        setSession({ token, roles: provisionedRoles(token), expired: false });
      }
    },
    signIn: async () => {
      await manager?.signinRedirect();
    },
    signOut: () => {
      setSession({ roles: [], expired: false });
      void manager?.removeUser();
      navigate('/sign-in');
    },
  };
  return (
    <AuthContext.Provider value={auth}>
      <ApiContext.Provider value={api}>{children}</ApiContext.Provider>
    </AuthContext.Provider>
  );
}
