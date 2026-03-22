export default function Field({
    label,
    placeholder,
    value,
    onChange,
    }: {
    label: string;
    placeholder: string;
    value: string;
    onChange: (v: string) => void;
}) {
    return (
    <label className="grid gap-1">
        <span className="text-sm font-medium text-slate-800">{label}</span>
        <input
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className="w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
        />
    </label>
    );
}