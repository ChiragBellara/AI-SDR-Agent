export default function Header() {
    return (
        <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
            <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-xl bg-slate-900" />
            <div className="text-sm font-semibold tracking-tight">
                AI-SDR
                <span className="ml-2 font-normal text-slate-500">Company Research</span>
            </div>
            </div>
            <div className="text-xs text-slate-500">v0.1</div>
        </div>
        </header>
    );
    }