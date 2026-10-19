import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../auth/session';
export function SignIn() {
  const auth = useAuth();
  const [failure, setFailure] = useState(false);
  const [busy, setBusy] = useState(false);
  return (
    <section className="auth-card">
      <div className="wordmark">
        aletheia
        <span />
      </div>
      <div className="eyebrow">EXPLAINABLE AI / ACCOUNTABLE DECISIONS</div>
      <h1>{auth.expired ? 'Your session has expired' : 'Clarity at every decision.'}</h1>
      <p>A decision-auditing workspace for case analysis and healthcare model evidence.</p>
      {!auth.configured && !auth.localAvailable && (
        <p className="notice">
          Organization sign-in is not configured in this environment. Public research evidence
          remains available.
        </p>
      )}
      {auth.localAvailable && (
        <p>
          <Link to="/local-session">Connect provisioned identity</Link>
        </p>
      )}
      {!auth.localAvailable && (
        <button
          className="button primary"
          disabled={!auth.configured || busy}
          onClick={() => {
            setBusy(true);
            void auth.signIn().catch(() => {
              setFailure(true);
              setBusy(false);
            });
          }}
        >
          Continue with organization SSO →
        </button>
      )}
      {failure && (
        <p role="alert">Sign-in could not be started. Try again or contact your organization.</p>
      )}
      <p>
        <Link to="/">Explore public evidence →</Link>
      </p>
      <small>No patient data is collected. Sessions are held in memory.</small>
    </section>
  );
}
