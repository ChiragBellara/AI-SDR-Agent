export default function Tabs({
    tabs,
    active,
    onChange,
    }: {
        tabs: string[];
        active: string;
        onChange: (t: string) => void;
    }) {
        return (
        <div className="flex flex-wrap gap-2 border-b border-slate-200">
            {tabs.map((t) => (
            <button
                key={t}
                onClick={() => onChange(t)}
                className={[
                "px-3 py-2 text-sm -mb-px border-b-2 transition",
                active === t ? "border-slate-900 text-slate-900" : "border-transparent text-slate-500 hover:text-slate-700",
                ].join(" ")}
            >
                {t}
            </button>
            ))}
        </div>
        );
    }