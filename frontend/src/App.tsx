import { Route, Routes } from 'react-router-dom';
import { lazy } from 'react';
import { Shell } from './components/Shell';
import { Overview } from './pages/Overview';
import { CaseAnalysis } from './pages/CaseAnalysis';
import { Explanation } from './pages/Explanation';
import { Reliability } from './pages/Reliability';
import { ReviewPage } from './pages/Review';
import { AuditTrail } from './pages/AuditTrail';
const ModelCard = lazy(() => import('./pages/ModelCard').then((m) => ({ default: m.ModelCard })));
const ReleaseEvidence = lazy(() =>
  import('./pages/ModelCard').then((m) => ({ default: m.ReleaseEvidence })),
);
import { SignIn } from './pages/SignIn';
import { NewAnalysis, SavedAnalysis, AnalysisHistory } from './pages/Analyses';
import { LocalSession } from './pages/LocalSession';
export function App() {
  return (
    <Routes>
      <Route element={<Shell />}>
        <Route index element={<Overview />} />
        <Route path="new-analysis" element={<NewAnalysis />} />
        <Route path="analyses" element={<AnalysisHistory />} />
        <Route path="analyses/:id" element={<SavedAnalysis />} />
        <Route path="local-session" element={<LocalSession />} />
        <Route path="demo" element={<CaseAnalysis />} />
        <Route path="predictions/:id" element={<CaseAnalysis />} />
        <Route path="predictions/:id/review" element={<ReviewPage />} />
        <Route path="review" element={<ReviewPage />} />
        <Route path="evidence/local" element={<Explanation />} />
        <Route path="evidence/global" element={<Explanation global />} />
        <Route path="evidence/stability" element={<Reliability />} />
        <Route path="evidence/subgroups" element={<Reliability area="subgroups" />} />
        <Route path="evidence/feasibility" element={<Reliability area="feasibility" />} />
        <Route path="audit-history" element={<AuditTrail />} />
        <Route path="audit-history/:eventId" element={<AuditTrail />} />
        <Route path="model-card" element={<ModelCard />} />
        <Route path="admin/models" element={<ReleaseEvidence />} />
        <Route path="admin/models/:version" element={<ReleaseEvidence />} />
        <Route path="sign-in" element={<SignIn />} />
        <Route
          path="auth/callback"
          element={<div role="status">Completing organization sign-in…</div>}
        />
        <Route
          path="*"
          element={
            <section>
              <h1>Page not found</h1>
              <p>Use the workspace navigation to open available evidence.</p>
            </section>
          }
        />
      </Route>
    </Routes>
  );
}
