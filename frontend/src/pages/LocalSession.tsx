import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/session';
import { errorCopy } from '../api/client';
import { PageHeading } from '../components/Shell';

export function LocalSession() {
  const auth = useAuth();
  const navigate = useNavigate();
  const [token, setToken] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>();
  return (
    <>
      <PageHeading
        title="Local provisioned identity"
        description="Use a short-lived access token provisioned by your local operator."
      />
      {!auth.localAvailable ? (
        <p>This build does not enable local provisioned sessions.</p>
      ) : (
        <form
          onSubmit={(e) => {
            e.preventDefault();
            if (busy || !token || !auth.connectLocal) return;
            setBusy(true);
            setError(undefined);
            void auth
              .connectLocal(token)
              .then(() => {
                setToken('');
                navigate('/new-analysis');
              })
              .catch((e) => {
                setError(e);
              })
              .finally(() => setBusy(false));
          }}
        >
          <label className="form-field">
            Provisioned access token
            <input
              type="password"
              autoComplete="off"
              required
              value={token}
              disabled={busy}
              onChange={(e) => setToken(e.target.value)}
            />
          </label>
          <button className="button primary" disabled={busy}>
            {busy ? 'Connecting…' : 'Connect local identity'}
          </button>
          {Boolean(error) && <p role="alert">{errorCopy(error)}</p>}
          <p className="small">
            The API verifies the signed token and existing entitlements. Tokens stay in memory and
            must be reconnected after refresh. No account is created.
          </p>
        </form>
      )}
    </>
  );
}
