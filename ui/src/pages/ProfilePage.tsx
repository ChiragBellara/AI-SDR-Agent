import { useMemo, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Card from "../components/Card";
import Tabs from "../components/Tabs";
import Button from "../components/Button";
import JsonViewer from "../components/JsonViewer";
import { getProfile } from "../client";

/* eslint-disable @typescript-eslint/no-explicit-any */
function downloadJson(filename: string, data: any) {
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
    }

    export default function ProfilePage() {
    const { jobId = "" } = useParams();
    const [tab, setTab] = useState("Overview");

    const q = useQuery({
        queryKey: ["profile-job-final", jobId],
        queryFn: () => getProfile(jobId),
        refetchInterval: false,
    });

    const data = q.data?.result;

    const tabs = useMemo(() => ["Overview", "Qualification", "Sources", "Raw JSON"], []);

    if (q.isLoading) return <div className="text-slate-600">Loading…</div>;
    if (!q.data) return <div className="text-slate-600">No data.</div>;

    if (q.data.status !== "completed") {
        return (
        <Card className="p-6">
            <div className="text-slate-800 font-medium">Profile not ready</div>
            <p className="mt-2 text-sm text-slate-600">This job is {q.data.status}. Go back to the run page.</p>
            <div className="mt-4">
            <Link className="text-sm underline" to={`/run/${jobId}`}>Back to progress</Link>
            </div>
        </Card>
        );
    }

    const company = data?.company;

    return (
        <div className="grid gap-6">
        <div className="flex items-start justify-between gap-4">
            <div>
            <h1 className="text-3xl font-semibold tracking-tight">{company?.name ?? "Company Profile"}</h1>
            <p className="mt-2 text-slate-600 max-w-2xl">
                {company?.description?.one_liner ?? "Generated profile output from your pipeline."}
            </p>
            </div>
            <div className="flex gap-2">
            <Button variant="ghost" onClick={() => downloadJson(`profile-${jobId}.json`, data)}>
                Download JSON
            </Button>
            <Link to="/"><Button>New</Button></Link>
            </div>
        </div>

        <Card className="p-6">
            <Tabs tabs={tabs} active={tab} onChange={setTab} />
            <div className="pt-5">
            {tab === "Overview" && (
                <div className="grid gap-4">
                <div className="grid gap-1">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Website</div>
                    <div className="text-sm text-slate-800">{company?.website}</div>
                </div>

                <div className="grid gap-1">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Positioning</div>
                    <div className="text-sm text-slate-800">{company?.description?.positioning}</div>
                </div>

                <div className="grid gap-1">
                    <div className="text-xs uppercase tracking-wide text-slate-500">Keywords</div>
                    <div className="flex flex-wrap gap-2">
                    {(company?.description?.keywords ?? []).map((k: string) => (
                        <span key={k} className="rounded-full border border-slate-200 bg-white px-3 py-1 text-xs text-slate-700">
                        {k}
                        </span>
                    ))}
                    </div>
                </div>
                </div>
            )}

            {tab === "Qualification" && (
                <div className="grid gap-4">
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4">
                    <div className="text-xs uppercase tracking-wide text-slate-500">ICP Fit</div>
                    <div className="mt-1 text-lg font-semibold">{data?.qualification?.icp_fit ?? "—"}</div>
                </div>

                <div className="grid gap-2">
                    <div className="text-sm font-medium text-slate-800">Reasons</div>
                    <div className="grid gap-2">
                    {(data?.qualification?.reasons ?? []).map((r: string, i: number) => (
                        <div key={i} className="rounded-xl border border-slate-200 p-3 text-sm text-slate-700">
                        {r}
                        </div>
                    ))}
                    </div>
                </div>

                <div className="grid gap-2">
                    <div className="text-sm font-medium text-slate-800">Risks</div>
                    <div className="grid gap-2">
                    {(data?.qualification?.risks ?? []).map((r: string, i: number) => (
                        <div key={i} className="rounded-xl border border-slate-200 p-3 text-sm text-slate-700">
                        {r}
                        </div>
                    ))}
                    </div>
                </div>
                </div>
            )}

            {tab === "Sources" && (
                <div className="grid gap-2">
                {(data?.sources ?? []).map((s: any, i: number) => (
                    <div key={i} className="rounded-xl border border-slate-200 p-3 text-sm">
                    <div className="text-slate-800">{s.url}</div>
                    <div className="text-slate-500 text-xs">{s.type}</div>
                    </div>
                ))}
                </div>
            )}

            {tab === "Raw JSON" && <JsonViewer data={data} />}
            </div>
        </Card>
        </div>
    );
}