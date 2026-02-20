import { useMemo } from "react";
import { TopBar } from "./components/TopBar"
import { PipelinePanel } from "./components/PipelinePanel"
import type { Step, Source } from "./types";

function App() {
  const steps: Step[] = useMemo(
    () => [
      { name: "Grounding", status: "Done", badge: "good", chips: ["3 pages", "2m 14s"] },
      { name: "Research", status: "Done", badge: "good", chips: ["12 queries", "1m 02s"] },
      { name: "Collector", status: "Running", badge: "warn", chips: ["18 sources", "blog + docs"] },
      { name: "Curator", status: "Queued", badge: "neutral", chips: ["dedupe", "rank"] },
      { name: "Analyzer", status: "Queued", badge: "neutral", chips: ["score", "recommend"] },
    ],
    []
  );
  
  const sources: Source[] = useMemo(
    () => [
      {
        url: "https://example.com/product/glean-assistant",
        snippet: "Assistant capabilities, knowledge access, deep research, and governance summary…",
      },
      {
        url: "https://example.com/platform/agents",
        snippet: "Agent Builder, orchestration, and library for workflow automation…",
      },
      {
        url: "https://example.com/security/glean-protect",
        snippet: "Permissions-aware access, content controls, and secure scaling claims…",
      },
    ],
    []
  );
  return (
      <div className="app">
        <TopBar company="Glean" status="Running" fit={8.2} />

        <main>
          <PipelinePanel steps={steps} sources={sources} />
          {/* <ReportPanel activeTab={activeTab} onTabChange={setActiveTab} />
          <NewRunPanel /> */}
        </main>
      </div>
  )
}

export default App