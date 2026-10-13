import { render, screen, waitFor, within } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import { App } from '../src/App';
import { ApiContext } from '../src/api/context';
import { ApiClient } from '../src/api/client';
import { AuthContext } from '../src/auth/session';
import {
  publicResponses,
  envelope,
  prediction,
  review,
  event,
  predictionId,
  eventId,
  jsonResponse,
  apiFailure,
} from './fixtures';

function setup(path = '/', roles: string[] = [], override?: typeof fetch) {
  const transport = vi.fn<typeof fetch>(async (url, options) => {
    const route = String(url).replace('/api/v1', '');
    if (override) {
      const response = await override(url, options);
      if (response) return response;
    }
    if (route === '/models/current') {
      const sample = structuredClone(publicResponses[route]) as {
        data: { approval_status: string; serving_available: boolean };
      };
      sample.data.approval_status = 'approved';
      sample.data.serving_available = true;
      return jsonResponse(sample);
    }
    if (route === '/health/ready')
      return jsonResponse({
        schema_version: 'application-v1',
        request_id: eventId,
        data: { status: 'ready' },
      });
    if (route === `/predictions/${predictionId}`)
      return jsonResponse(envelope(prediction, 'synthetic_inference'));
    if (route === `/predictions/${predictionId}/reviews`)
      return jsonResponse(
        envelope(
          options?.method === 'POST' ? review : { items: [], next_cursor: null },
          'synthetic_inference',
        ),
        options?.method === 'POST' ? 201 : 200,
      );
    if (route.startsWith('/audit-events?'))
      return jsonResponse(
        envelope({
          items: [event, { ...event, id: predictionId, event_type: 'review_created', sequence: 6 }],
          next_cursor: '5',
        }),
      );
    if (route === `/audit-events/${eventId}`) return jsonResponse(envelope(event));
    if (route === '/predictions')
      return jsonResponse(envelope(prediction, 'synthetic_inference'), 201);
    return route in publicResponses
      ? jsonResponse(publicResponses[route])
      : apiFailure(404, 'not_found');
  });
  const auth = {
    token: roles.length ? 'test-token' : undefined,
    roles,
    expired: false,
    configured: false,
    signIn: vi.fn(async () => {}),
    signOut: vi.fn(),
  };
  const api = new ApiClient('/api/v1', () => auth.token, undefined, transport);
  render(
    <MemoryRouter initialEntries={[path]}>
      <AuthContext.Provider value={auth}>
        <ApiContext.Provider value={api}>
          <App />
        </ApiContext.Provider>
      </AuthContext.Provider>
    </MemoryRouter>,
  );
  return { transport, user: userEvent.setup(), auth };
}
describe('evidence workbench', () => {
  it('renders backend overview and navigates with keyboard focus', async () => {
    const { user } = setup();
    expect(await screen.findByText('12.78', { exact: false })).toBeVisible();
    expect(screen.getByText('approved')).toBeVisible();
    await user.click(screen.getByRole('link', { name: 'Case Analysis' }));
    expect(await screen.findByRole('heading', { name: 'Case Analysis', level: 1 })).toBeVisible();
    expect(screen.getByRole('main')).toHaveFocus();
    expect(
      await screen.findByText('Inputs are fixed on the server and cannot be edited.'),
    ).toBeVisible();
    expect(screen.queryByRole('spinbutton')).not.toBeInTheDocument();
  });
  it('renders signed explanation, baseline and noncausal calibration semantics', async () => {
    setup('/evidence/local');
    expect(await screen.findByText('0.10847551')).toBeVisible();
    expect(screen.getAllByText('Raises', { exact: true, selector: 'td' }).length).toBeGreaterThan(
      0,
    );
    expect(screen.getAllByText('Lowers').length).toBeGreaterThan(0);
    expect(screen.getByText(/Calibration is not an additional/)).toBeVisible();
    expect(screen.getByRole('table')).toHaveAccessibleName(
      'Source-field contributions in probability units',
    );
  });
  it('shows global repeat evidence and source fields', async () => {
    setup('/evidence/global');
    expect(await screen.findByRole('table')).toHaveAccessibleName(
      'Mean absolute contributions in calibrated-probability units',
    );
    expect(screen.getAllByText(/not confidence intervals/).length).toBeGreaterThan(0);
  });
  it('shows missing evidence explicitly and never fabricates a result', async () => {
    setup('/evidence/local', [], async () => apiFailure(404, 'not_found'));
    expect(await screen.findByRole('alert')).toHaveTextContent('absent');
    expect(screen.queryByText('0.10847551')).not.toBeInTheDocument();
  });
  it('renders stability and undefined crossing evidence', async () => {
    setup('/evidence/stability');
    expect(await screen.findByText('80')).toBeVisible();
    expect(screen.getByText(/Crossing-only summary metrics are unavailable/)).toBeVisible();
  });
  it('preserves subgroup counts, uncertainty, suppression and metric selection', async () => {
    const { user } = setup('/evidence/subgroups');
    expect(await screen.findByText(/AfricanAmerican/)).toBeVisible();
    expect(screen.getAllByText(/insufficient support/).length).toBeGreaterThan(0);
    expect(screen.getAllByText(/<20/).length).toBeGreaterThan(0);
    await user.selectOptions(screen.getByLabelText('Published metric'), 'recall');
    expect(screen.getByRole('table')).toHaveTextContent('recall');
    expect(screen.getByText(/not fairness certification/)).toBeVisible();
  });
  it('treats no feasible scenario as a valid result', async () => {
    setup('/evidence/feasibility');
    expect(await screen.findByText('Valid feasibility result')).toBeVisible();
    expect(
      screen.getByText('No search was performed and no candidates were returned.'),
    ).toBeVisible();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
  });
  it('shows unavailable model metadata without calling it revoked or approved', async () => {
    setup('/model-card', [], async (url) =>
      String(url).endsWith('/models/current')
        ? jsonResponse(publicResponses['/models/current'])
        : (undefined as unknown as Response),
    );
    expect(
      await screen.findByText(
        /does not identify whether the cause is revocation/,
        {},
        { timeout: 5000 },
      ),
    ).toBeVisible();
    expect(screen.queryByText('approved', { exact: true })).not.toBeInTheDocument();
    expect(await screen.findByText(/Published card SHA/)).toBeVisible();
  });
  it('allows administrator release evidence only for its explicit role', async () => {
    setup('/admin/models', ['engineer']);
    expect(await screen.findByText('Administrator permission is required.')).toBeVisible();
    expect(screen.queryByRole('link', { name: 'Release evidence' })).not.toBeInTheDocument();
  });
  it('keeps sign-in unavailable without provider configuration', () => {
    setup('/sign-in');
    expect(screen.getByRole('button', { name: /Continue with organization/ })).toBeDisabled();
    expect(screen.getByText(/not configured/)).toBeVisible();
  });
  it('keeps network failure visible without fixture fallback', async () => {
    setup('/', [], async () => {
      throw new TypeError('offline');
    });
    expect((await screen.findAllByRole('alert'))[0]).toHaveTextContent('No substitute results');
    expect(screen.queryByText('12.78', { exact: false })).not.toBeInTheDocument();
  });
  it('disables prediction on audit identity mismatch', async () => {
    setup('/demo', ['engineer'], async (url) => {
      if (String(url).endsWith('/demo/cases')) {
        const raw = structuredClone(publicResponses['/demo/cases']) as {
          evidence: { audit_results_sha256: string };
        };
        raw.evidence.audit_results_sha256 = 'f'.repeat(64);
        return jsonResponse(raw);
      }
      return undefined as unknown as Response;
    });
    await screen.findByText('40');
    expect(screen.getByRole('button', { name: 'Create audited prediction' })).toBeDisabled();
  });
  it('persists a prediction then shows its timestamp and audit reference', async () => {
    const { user, transport } = setup('/demo', ['engineer']);
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Create audited prediction' })).toBeEnabled(),
    );
    await user.click(screen.getByRole('button', { name: 'Create audited prediction' }));
    expect(await screen.findByText(prediction.created_at)).toBeVisible();
    expect(screen.getByRole('link', { name: /Prediction audit event/ })).toHaveAttribute(
      'href',
      '/audit-history/' + eventId,
    );
    const call = transport.mock.calls.find(([, opts]) => opts?.method === 'POST');
    expect(JSON.parse(String(call?.[1]?.body))).toEqual({
      schema_version: 'application-v1',
      case_id: 'synthetic-discharge-v1',
      model_version: '1',
    });
  });
});
describe('reviews and audit', () => {
  async function fillReview(user: ReturnType<typeof userEvent.setup>) {
    await screen.findByRole('button', { name: 'Submit coded review' });
    for (const checkbox of screen.getAllByRole('checkbox')) await user.click(checkbox);
    await user.selectOptions(screen.getByLabelText('Required coded reason'), 'evidence_reviewed');
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Submit coded review' })).toBeEnabled(),
    );
  }
  it('requires the evidence checklist before persistence', async () => {
    const { user, transport } = setup(`/predictions/${predictionId}/review`, ['reviewer']);
    await screen.findByRole('button', { name: 'Submit coded review' });
    await user.selectOptions(screen.getByLabelText('Required coded reason'), 'evidence_reviewed');
    await user.click(screen.getByRole('button', { name: 'Submit coded review' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Check each evidence item');
    expect(transport.mock.calls.some(([, opts]) => opts?.method === 'POST')).toBe(false);
  });
  it('confirms real HTTP success and links the review audit', async () => {
    const { user, transport } = setup(`/predictions/${predictionId}/review`, ['reviewer']);
    await fillReview(user);
    await user.click(screen.getByRole('button', { name: 'Submit coded review' }));
    expect(await screen.findByText(/Review persisted/)).toBeVisible();
    expect(screen.getByRole('link', { name: /Inspect linked audit event/ })).toHaveAttribute(
      'href',
      '/audit-history/' + eventId,
    );
    const call = transport.mock.calls.find(([, opts]) => opts?.method === 'POST');
    expect(JSON.parse(String(call?.[1]?.body))).toMatchObject({
      expected_revision: 0,
      reason_code: 'evidence_reviewed',
    });
  });
  it('retains exact retry identity on an uncertain outcome', async () => {
    let writes = 0;
    const { user, transport } = setup(
      `/predictions/${predictionId}/review`,
      ['reviewer'],
      async (_url, opts) =>
        opts?.method === 'POST'
          ? ++writes === 1
            ? apiFailure(504, 'deadline_exceeded')
            : jsonResponse(envelope(review, 'synthetic_inference'), 201)
          : (undefined as unknown as Response),
    );
    await fillReview(user);
    await user.click(screen.getByRole('button', { name: 'Submit coded review' }));
    await screen.findByRole('alert');
    expect(screen.queryByText(/Review persisted/)).not.toBeInTheDocument();
    expect(screen.getByLabelText('Required coded reason')).toBeDisabled();
    await user.click(screen.getByRole('button', { name: 'Retry same review' }));
    await screen.findByText(/Review persisted/);
    const posts = transport.mock.calls.filter(([, opts]) => opts?.method === 'POST');
    expect(posts[0]?.[1]?.body).toEqual(posts[1]?.[1]?.body);
    expect((posts[0]?.[1]?.headers as Record<string, string>)['Idempotency-Key']).toEqual(
      (posts[1]?.[1]?.headers as Record<string, string>)['Idempotency-Key'],
    );
  });
  it('shows a conflict without claiming success and supports refresh', async () => {
    const { user } = setup(
      `/predictions/${predictionId}/review`,
      ['reviewer'],
      async (_url, opts) =>
        opts?.method === 'POST'
          ? apiFailure(409, 'revision_conflict')
          : (undefined as unknown as Response),
    );
    await fillReview(user);
    await user.click(screen.getByRole('button', { name: 'Submit coded review' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('revision');
    expect(screen.queryByText(/Review persisted/)).not.toBeInTheDocument();
    await user.click(
      screen.getByRole('button', { name: 'Refresh history and start a new submission' }),
    );
    await waitFor(() =>
      expect(screen.getByRole('button', { name: 'Submit coded review' })).toBeEnabled(),
    );
  });
  it.each([['engineer'], ['administrator']])(
    'denies review to %s without reviewer role',
    async (role) => {
      setup(`/predictions/${predictionId}/review`, [role]);
      expect(await screen.findByRole('button', { name: 'Submit coded review' })).toBeDisabled();
      expect(screen.getByText(/do not grant reviewer permission/)).toBeVisible();
    },
  );
  it('shows backend forbidden even when the token hints reviewer', async () => {
    const { user } = setup(
      `/predictions/${predictionId}/review`,
      ['reviewer'],
      async (_url, opts) =>
        opts?.method === 'POST'
          ? apiFailure(403, 'role_required')
          : (undefined as unknown as Response),
    );
    await fillReview(user);
    await user.click(screen.getByRole('button', { name: 'Submit coded review' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('does not have access');
    expect(screen.queryByText(/Review persisted/)).not.toBeInTheDocument();
  });
  it('filters only the loaded audit page and opens authorized detail', async () => {
    const { user, transport } = setup('/audit-history', ['engineer']);
    await screen.findByRole('table');
    await user.selectOptions(
      screen.getByLabelText('Filter loaded page by event type'),
      'prediction_created',
    );
    expect(screen.getAllByRole('link', { name: 'Inspect event' })).toHaveLength(1);
    await user.click(screen.getByRole('link', { name: 'Inspect event' }));
    expect(await screen.findByText(event.event_hash)).toBeVisible();
    expect(screen.getByText('Actor role')).toBeVisible();
    expect(screen.getAllByText('Not published')).toHaveLength(2);
    expect(
      transport.mock.calls.some(([url]) => String(url).endsWith('/audit-events/' + eventId)),
    ).toBe(true);
  });
  it('uses the API cursor for bounded older audit pages', async () => {
    const { user, transport } = setup('/audit-history', ['engineer']);
    await user.click(await screen.findByRole('button', { name: 'Older events →' }));
    await waitFor(() =>
      expect(transport.mock.calls.some(([url]) => String(url).includes('&cursor=5'))).toBe(true),
    );
  });
  it('keeps audit inaccessible to a public viewer', () => {
    setup('/audit-history');
    expect(screen.getByRole('link', { name: /Sign in to inspect audit/ })).toBeVisible();
  });
  it('keeps accessible text alternatives for contribution charts', async () => {
    setup('/evidence/local');
    const table = await screen.findByRole('table');
    expect(within(table).getAllByRole('row')).toHaveLength(14);
  });
});
