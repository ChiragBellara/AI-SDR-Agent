type Step = {
    node: string;
    message: string;
    done: boolean;
};

// Ordered list of nodes so we can show pending ones too
const ORDERED_NODES = [
    { node: "grounding",            label: "Crawling website" },
    { node: "triggers_researcher",  label: "Scanning sales triggers" },
    { node: "offering_researcher",  label: "Analyzing offerings" },
    { node: "readiness_researcher", label: "Checking B2B readiness" },
    { node: "customer_researcher",  label: "Profiling customers" },
    { node: "news_analyst",         label: "Gathering news" },
    { node: "collector",            label: "Aggregating research" },
    { node: "persona",              label: "Synthesizing persona" },
];

type Props = {
    completedSteps: Step[];
    company: string;
};

export default function ProgressPanel({ completedSteps, company }: Props) {
    const doneNodes = new Set(completedSteps.map((s) => s.node));
    // The active node is the first one not yet done
    const activeIndex = ORDERED_NODES.findIndex((n) => !doneNodes.has(n.node));

    return (
        <div className="flex h-full flex-col items-center justify-center px-10">
            <div className="w-full max-w-sm">
                <p className="mb-6 text-sm font-medium text-slate-700">
                    Researching{" "}
                    <span className="font-semibold">{company}</span>…
                </p>

                <ol className="space-y-3">
                    {ORDERED_NODES.map(({ node, label }, i) => {
                        const done = doneNodes.has(node);
                        const active = i === activeIndex;
                        const pending = !done && !active;

                        // find the actual message if done
                        const stepMsg = completedSteps.find(
                            (s) => s.node === node,
                        )?.message;

                        return (
                            <li key={node} className="flex items-start gap-3">
                                {/* Icon */}
                                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center">
                                    {done ? (
                                        <svg
                                            className="h-4 w-4 text-emerald-500"
                                            viewBox="0 0 20 20"
                                            fill="currentColor"
                                        >
                                            <path
                                                fillRule="evenodd"
                                                d="M16.704 4.153a.75.75 0 0 1 .143 1.052l-8 10.5a.75.75 0 0 1-1.127.075l-4.5-4.5a.75.75 0 0 1 1.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 0 1 1.05-.143Z"
                                                clipRule="evenodd"
                                            />
                                        </svg>
                                    ) : active ? (
                                        <span className="relative flex h-3 w-3">
                                            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-slate-400 opacity-75" />
                                            <span className="relative inline-flex h-3 w-3 rounded-full bg-slate-600" />
                                        </span>
                                    ) : (
                                        <span className="h-2 w-2 rounded-full bg-slate-200" />
                                    )}
                                </span>

                                {/* Label */}
                                <span
                                    className={
                                        done
                                            ? "text-sm text-slate-500"
                                            : active
                                              ? "text-sm font-medium text-slate-900"
                                              : "text-sm text-slate-300"
                                    }
                                >
                                    {done && stepMsg ? stepMsg : label}
                                </span>
                            </li>
                        );
                    })}
                </ol>
            </div>
        </div>
    );
}
