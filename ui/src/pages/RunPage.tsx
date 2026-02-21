import { useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import Card from "../components/Card";
import Stepper from "../components/Stepper";
import { getProfile } from "../client";

export default function RunPage() {
    const { jobId = "" } = useParams();
    const nav = useNavigate();

    const q = useQuery({
        queryKey: ["profile-job", jobId],
        queryFn: () => getProfile(jobId),
        refetchInterval: (data) => {
        if (!data) return 1000;
        },
    });

    useEffect(() => {
        if (q.data?.status === "completed") nav(`/profile/${jobId}`);
    }, [q.data?.status, jobId, nav]);

    const job = q.data;

    return (
        <div className="grid gap-6">
        <div>
            <h1 className="text-2xl font-semibold tracking-tight">Generating profile</h1>
            <p className="mt-2 text-slate-600">Job ID: <span className="font-mono text-slate-700">{jobId}</span></p>
        </div>

        <Card className="p-6 grid gap-4">
            <div className="flex items-center justify-between gap-4">
            <div className="text-sm">
                <div className="text-slate-700 font-medium">{job?.progress?.message ?? "Loading..."}</div>
                <div className="text-slate-500">{job?.status ?? "…"}</div>
            </div>
            <div className="text-sm text-slate-700 font-medium">{job?.progress?.percent ?? 0}%</div>
            </div>

            <div className="h-2 rounded-full bg-slate-100 overflow-hidden">
            <div
                className="h-2 bg-slate-900 transition-all"
                style={{ width: `${job?.progress?.percent ?? 0}%` }}
            />
            </div>

            <Stepper stage={job?.progress?.stage ?? "queued"} />

            {job?.status === "failed" && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {job.error ?? "Job failed."}
            </div>
            )}
        </Card>

        <Card className="p-6">
            <div className="text-sm text-slate-700 font-medium">UX note</div>
            <p className="mt-2 text-sm text-slate-600">
            Polling is simplest. If you want “real-time logs”, switch to SSE later, but keep the same UI layout.
            </p>
        </Card>
        </div>
    );
}