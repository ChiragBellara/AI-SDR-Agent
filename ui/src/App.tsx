import { Routes, Route, Navigate, Link } from "react-router-dom";
import NewProfilePage from "./pages/NewProfilePage";
import RunPage from "./pages/RunPage";
import ProfilePage from "./pages/ProfilePage";

export default function App() {
  return (
    <div className="min-h-screen bg-white text-slate-900">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
          <Link to="/" className="font-semibold tracking-tight">
            AI-SDR <span className="text-slate-500 font-normal">Profiles</span>
          </Link>
          <div className="text-sm text-slate-600">Minimal clean SaaS scaffold</div>
        </div>
      </header>

      <main className="mx-auto max-w-5xl px-4 py-10">
        <Routes>
          <Route path="/" element={<NewProfilePage />} />
          <Route path="/run/:jobId" element={<RunPage />} />
          <Route path="/profile/:jobId" element={<ProfilePage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <footer className="border-t border-slate-200">
        <div className="mx-auto max-w-5xl px-4 py-6 text-xs text-slate-500">
          Tip: Replace the backend fake pipeline with your LangGraph workflow output.
        </div>
      </footer>
    </div>
  );
}