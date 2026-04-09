export default function Field({
    label,
    placeholder,
    value,
    onChange,
    required = false,
    multiline = false,
    rows = 1,
}: {
    label: string;
    placeholder: string;
    value: string;
    onChange: (v: string) => void;
    required?: boolean;
    multiline?: boolean;
    rows?: number;
}) {
    return (
        <label className="grid gap-1">
            <span className="text-sm font-medium text-slate-800">
                {label}
                {required ? (
                    <span className="ml-1 text-red-500 text-xs">*</span>
                ) : (
                    <span className="ml-1 text-slate-400 text-xs">
                        (optional)
                    </span>
                )}
            </span>
            {multiline ? (
                <textarea
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder}
                    required={required}
                    rows={rows}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200 resize-y"
                />
            ) : (
                <input
                    value={value}
                    onChange={(e) => onChange(e.target.value)}
                    placeholder={placeholder}
                    required={required}
                    className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
                />
            )}
        </label>
    );
}
