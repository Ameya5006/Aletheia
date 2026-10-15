import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { App } from '../src/App';
import { AuthContext } from '../src/auth/session';
import { ApiContext } from '../src/api/context';
import { ApiClient } from '../src/api/client';
import { envelope, jsonResponse, apiFailure, publicResponses } from './fixtures';
import fixture from './case-fixtures.json';

function setup(path = '/new-analysis', fail: boolean | number = false, delay?: Promise<void>) {
  const calls: { path: string; body: unknown; key: string | null }[] = [];
  let saved = false;
  const transport = vi.fn<typeof fetch>(async (url, options) => {
    const path = String(url).replace('/api/v1', '');
    if (options?.body)
      calls.push({
        path,
        body: JSON.parse(String(options.body)),
        key: new Headers(options.headers).get('Idempotency-Key'),
      });
    if (path === '/analyses/schema') return jsonResponse(envelope(fixture.mapping));
    if (path === '/models/current')
      return jsonResponse({
        ...(publicResponses[path] as object),
        data: {
          domain: 'healthcare',
          target: 'readmitted_30d',
          family: 'histogram',
          calibration: 'sigmoid',
          feature_policy_version: 'healthcare-feature-v1',
          threshold: 0.5,
          approval_status: 'approved',
          serving_available: true,
        },
      });
    if (path === '/analyses' && options?.method === 'POST') {
      await delay;
      if (fail === 502) return jsonResponse(envelope({ probability: 'invalid' }, 'case_inference'));
      return fail
        ? apiFailure(typeof fail === 'number' ? fail : 503)
        : jsonResponse(envelope({ ...fixture.result, saved }, 'case_inference'), 201);
    }
    if (path.endsWith('/save')) saved = true;
    if (path.startsWith('/analyses/'))
      return jsonResponse(envelope({ ...fixture.result, saved }, 'case_inference'));
    if (path.startsWith('/analyses'))
      return jsonResponse(
        envelope({ items: saved ? [{ ...fixture.result, saved }] : [], next_cursor: null }),
      );
    return apiFailure(404);
  });
  const api = new ApiClient('/api/v1', () => 'test-token', undefined, transport);
  render(
    <MemoryRouter initialEntries={[path]}>
      <AuthContext.Provider
        value={{
          token: 'test-token',
          roles: ['engineer'],
          expired: false,
          configured: false,
          signIn: async () => {},
          signOut: () => {},
        }}
      >
        <ApiContext.Provider value={api}>
          <App />
        </ApiContext.Provider>
      </AuthContext.Provider>
    </MemoryRouter>,
  );
  return { calls, transport, user: userEvent.setup() };
}

async function fill(user: ReturnType<typeof userEvent.setup>) {
  await screen.findByLabelText('Admission type');
  for (const f of fixture.mapping.fields) {
    const value = fixture.result.inputs[f.field as keyof typeof fixture.result.inputs];
    if (f.control === 'number') await user.type(screen.getByLabelText(f.label), value);
    else await user.selectOptions(screen.getByLabelText(f.label), value);
  }
}

describe('entered case workflow', () => {
  it('renders all thirteen empty accessible controls, options, errors and reset', async () => {
    const { user, calls } = setup();
    await screen.findByLabelText('Admission type');
    expect(screen.getAllByRole('spinbutton')).toHaveLength(8);
    expect(screen.getAllByRole('combobox')).toHaveLength(5);
    expect(screen.getByLabelText('Admission type')).toHaveValue('');
    expect(screen.getByRole('option', { name: 'Elective' })).toHaveValue('3');
    await user.click(screen.getByRole('button', { name: 'Run Analysis' }));
    expect(await screen.findByText('Check the highlighted fields.')).toBeVisible();
    expect(calls).toHaveLength(0);
    await user.type(screen.getByLabelText('Time in hospital'), '15');
    await user.click(screen.getByRole('button', { name: 'Run Analysis' }));
    expect(screen.getByText(/Enter a whole number from 1 to 14/)).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Reset Form' }));
    expect(screen.getByLabelText('Time in hospital')).toHaveValue(null);
    expect(screen.queryByText('Check the highlighted fields.')).not.toBeInTheDocument();
  });
  it('submits entered values, displays evidence, saves and loads inputs into a new form', async () => {
    const { user, calls } = setup();
    await fill(user);
    await user.click(screen.getByRole('button', { name: 'Run Analysis' }));
    expect(await screen.findByRole('heading', { name: 'Prediction Result' })).toBeVisible();
    expect(calls[0]?.body).toMatchObject({
      schema_version: 'case-input-v1',
      inputs: { number_inpatient: 4 },
    });
    expect(screen.getByText(fixture.result.prediction_id)).toBeVisible();
    expect(screen.getByText(fixture.result.event_id)).toBeVisible();
    expect(screen.getByText(/Model-level stability/)).toBeVisible();
    expect(screen.getByRole('table', { name: 'Factors increasing the output' })).toBeVisible();
    expect(screen.getByRole('table', { name: 'Factors decreasing the output' })).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Save Analysis' }));
    expect(await screen.findByText('Saved')).toBeVisible();
    await user.click(screen.getByRole('link', { name: 'Analysis History' }));
    await user.click(await screen.findByRole('link', { name: /Open analysis/ }));
    expect(await screen.findByText(fixture.result.prediction_id)).toBeVisible();
    await user.click(screen.getByRole('button', { name: 'Load inputs into New Analysis' }));
    expect(await screen.findByLabelText('Inpatient visits in the preceding year')).toHaveValue(4);
    expect(screen.queryByRole('heading', { name: 'Prediction Result' })).not.toBeInTheDocument();
    expect(calls.filter((c) => c.path === '/analyses')).toHaveLength(1);
  });
  it('preserves inputs and the submission key after recoverable errors', async () => {
    const { user, calls } = setup('/new-analysis', true);
    await fill(user);
    await user.click(screen.getByRole('button', { name: 'Run Analysis' }));
    await screen.findByRole('alert');
    expect(screen.getByLabelText('Inpatient visits in the preceding year')).toHaveValue(4);
    await user.click(screen.getByRole('button', { name: 'Retry same analysis' }));
    await waitFor(() => expect(calls).toHaveLength(2));
    expect(calls[0]?.key).toBe(calls[1]?.key);
  });
  it.each([401, 403, 502])(
    'rejects authentication, authorization or invalid-response failure %s',
    async (status) => {
      const { user } = setup('/new-analysis', status);
      await fill(user);
      await user.click(screen.getByRole('button', { name: 'Run Analysis' }));
      expect(await screen.findByRole('alert')).toBeVisible();
      expect(screen.queryByRole('heading', { name: 'Prediction Result' })).not.toBeInTheDocument();
    },
  );
  it('prevents duplicate submission while an analysis is running', async () => {
    let complete!: () => void;
    const delay = new Promise<void>((resolve) => {
      complete = resolve;
    });
    const { user, calls } = setup('/new-analysis', false, delay);
    await fill(user);
    await user.dblClick(screen.getByRole('button', { name: 'Run Analysis' }));
    expect(screen.getByRole('button', { name: 'Running…' })).toBeDisabled();
    expect(calls).toHaveLength(1);
    complete();
    await screen.findByRole('heading', { name: 'Prediction Result' });
  });
});
