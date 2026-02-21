/* eslint-disable @typescript-eslint/no-explicit-any */
export default function JsonViewer({ data }: { data: any }) {
    return (
        <pre className="overflow-auto rounded-2xl border border-slate-200 bg-slate-50 p-4 text-xs leading-relaxed">
            {JSON.stringify(data, null, 2)}
        </pre>
        );
    }