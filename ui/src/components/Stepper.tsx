const ORDER = ["queued", "grounding", "research", "collect", "curate", "analyze", "finalize", "done"];

export default function Stepper({ stage }: { stage: string }) {
    const currentIdx = Math.max(0, ORDER.indexOf(stage));

    return (
        <div className="flex flex-wrap gap-2">
        {ORDER.map((s, idx) => {
            const active = idx <= currentIdx;
            return (
            <div
                key={s}
                className={[
                "rounded-full border px-3 py-1 text-xs",
                active ? "border-slate-900 bg-slate-900 text-white" : "border-slate-200 text-slate-600",
                ].join(" ")}
            >
                {s}
            </div>
            );
        })}
        </div>
    );
}