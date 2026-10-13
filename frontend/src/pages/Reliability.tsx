import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useResource } from '../api/context';
import { stabilitySchema, subgroupsSchema, feasibilitySchema } from '../api/contracts';
import { PageHeading } from '../components/Shell';
import {
  fieldLabel,
  Metric,
  number,
  Notice,
  Panel,
  Provenance,
  ResourceState,
} from '../components/ui';
export function Reliability({
  area = 'stability',
}: {
  area?: 'stability' | 'subgroups' | 'feasibility';
}) {
  const stability = useResource(
    area === 'stability' ? '/audits/stability' : undefined,
    stabilitySchema,
  );
  const groups = useResource(
    area === 'subgroups' ? '/audits/subgroups' : undefined,
    subgroupsSchema,
  );
  const feasibility = useResource(
    area === 'feasibility' ? '/counterfactuals/feasibility' : undefined,
    feasibilitySchema,
  );
  const [metric, setMetric] = useState('roc_auc');
  const resource = area === 'stability' ? stability : area === 'subgroups' ? groups : feasibility;
  const s = stability.value?.data;
  const f = feasibility.value?.data;
  return (
    <>
      <PageHeading
        title="Reliability"
        description="Assess the stability and boundaries of the published model evidence."
      />
      <div className="tabs">
        {[
          ['stability', 'Explanation stability'],
          ['subgroups', 'Subgroup evidence'],
          ['feasibility', 'Counterfactual feasibility'],
        ].map(([key, label]) => (
          <Link key={key} to={'/evidence/' + key} aria-current={area === key ? 'page' : undefined}>
            {label}
          </Link>
        ))}
      </div>
      <ResourceState
        loading={resource.loading}
        error={resource.error}
        retry={resource.reload}
        empty={!resource.value}
      />
      {s && (
        <>
          <div className="metric-grid">
            <Metric label="Recording comparisons" value={s.comparisons} caption={s.population} />
            <Metric
              label="Mean top-k overlap"
              value={number(s.all.top_k_overlap.mean)}
              caption={`Minimum ${number(s.all.top_k_overlap.min)}`}
            />
            <Metric
              label="Boundary crossings"
              value={s.boundary_crossings}
              caption="At the unchanged descriptive threshold"
            />
          </div>
          <Panel title="Stability measurements">
            <div className="table-scroll">
              <table>
                <caption>Published recording-sensitivity summaries</caption>
                <thead>
                  <tr>
                    <th>Measurement</th>
                    <th>Mean</th>
                    <th>Minimum</th>
                    <th>Maximum</th>
                    <th>Undefined</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(s.all).map(([key, v]) => (
                    <tr key={key}>
                      <th scope="row">{fieldLabel(key)}</th>
                      <td>{number(v.mean)}</td>
                      <td>{number(v.min)}</td>
                      <td>{number(v.max)}</td>
                      <td>{v.undefined}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p>
              Mean absolute probability change {number(s.mean_absolute_probability_change, 6)};
              maximum {number(s.max_absolute_probability_change, 6)}.
            </p>
            <p>
              {s.below_overlap_reference} below the protocol overlap reference;{' '}
              {s.above_distance_reference} above the distance reference; {s.unchanged_at_bound}{' '}
              unchanged at bounds.
            </p>
            <dl className="facts">
              {Object.entries(s.bounds).map(([key, range]) => (
                <div key={key}>
                  <dt>{fieldLabel(key)} bounds</dt>
                  <dd>{range.join('–')}</dd>
                </div>
              ))}
            </dl>
            {s.boundary_crossings === 0 && (
              <Notice>
                No class-crossing comparisons occurred. Crossing-only summary metrics are
                unavailable, not zero-valued effects.
              </Notice>
            )}
            <Notice tone="warning">{s.limitations}</Notice>
          </Panel>
        </>
      )}
      {groups.value && (
        <Panel title="Support-aware subgroup evidence">
          <Notice tone="warning">
            Observed subgroup differences are not fairness certification. Patient-cluster intervals
            describe this historical cohort. Zero observed events and [0,0] intervals do not prove a
            population rate of zero.
          </Notice>
          <label className="form-field">
            Published metric
            <select value={metric} onChange={(e) => setMetric(e.target.value)}>
              {[
                'roc_auc',
                'average_precision',
                'brier_score',
                'recall',
                'specificity',
                'false_positive_rate',
                'false_negative_rate',
                'positive_prediction_rate',
                'prevalence',
              ].map((key) => (
                <option key={key} value={key}>
                  {fieldLabel(key)}
                </option>
              ))}
            </select>
          </label>
          <div className="table-scroll">
            <table>
              <caption>Subgroup estimates, sample sizes and 95% patient-cluster intervals</caption>
              <thead>
                <tr>
                  <th>Attribute / group</th>
                  <th>Encounters / patients</th>
                  <th>Positive / negative</th>
                  <th>{fieldLabel(metric)}</th>
                  <th>Interval / replicates</th>
                  <th>Evidence status</th>
                </tr>
              </thead>
              <tbody>
                {groups.value.data.map((group) => {
                  const u = group.uncertainty?.[metric];
                  return (
                    <tr key={group.attribute + group.group}>
                      <th scope="row">
                        {group.attribute} / {group.group}
                      </th>
                      <td>
                        {group.counts.encounters} / {group.counts.patients}
                      </td>
                      <td>
                        {group.counts.positive} / {group.counts.negative}
                      </td>
                      <td>{number(group.metrics?.[metric], 6)}</td>
                      <td>
                        {u?.interval
                          ? u.interval.map((v) => number(v, 6)).join('–')
                          : 'Not available'}
                        {u && (
                          <small>
                            {u.valid_replicates} valid; {u.undefined_replicates} undefined
                          </small>
                        )}
                      </td>
                      <td>
                        {fieldLabel(group.status)}
                        {group.reason && <small>{group.reason}</small>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          {groups.value.data.length === 0 && (
            <Notice>No subgroup evidence has been published.</Notice>
          )}
        </Panel>
      )}
      {f && (
        <Panel title="No feasible scenario">
          <span className="chip">Valid feasibility result</span>
          <h2>History is not an intervention.</h2>
          <p>{f.assessment.reason}</p>
          <p>{f.worked_example}</p>
          <div className="two-columns">
            <div>
              <h3>Admissible changes</h3>
              <p>
                {f.assessment.mutable.length} mutable; {f.assessment.conditionally_mutable.length}{' '}
                conditionally mutable fields.
              </p>
              <p>No search was performed and no candidates were returned.</p>
            </div>
            <div>
              <h3>Distance and cost</h3>
              <p>{f.assessment.distance_reason}</p>
              <p>{f.assessment.limitations}</p>
            </div>
          </div>
          <details>
            <summary>Immutable and excluded fields</summary>
            <p>Immutable: {f.assessment.immutable.map(fieldLabel).join(', ')}</p>
            <p>Excluded: {f.assessment.excluded.map(fieldLabel).join(', ')}</p>
          </details>
        </Panel>
      )}
      <Provenance evidence={resource.value?.evidence} />
    </>
  );
}
