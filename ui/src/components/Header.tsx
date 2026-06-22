import { useState } from "react";
import { NavLink } from "react-router-dom";
import { clearCache } from "../client";

export default function Header() {
    const [clearing, setClearing] = useState(false);

    const handleClearCache = () => {
        setClearing(true);
        clearCache();
        setClearing(false);
    };

    return (
        <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur">
            <div className="mx-auto flex max-w-5xl items-center justify-between px-4 py-3">
                <div className="flex items-center gap-2">
                    <div className="h-8 w-8 rounded-xl bg-slate-900" />
                    <div className="text-sm font-semibold tracking-tight">
                        AI-SDR
                    </div>
                </div>

                <nav className="flex items-center gap-1">
                    <NavLink
                        to="/"
                        end
                        className={({ isActive }) =>
                            `px-3 py-1.5 text-sm transition-colors rounded-lg ${
                                isActive
                                    ? "font-medium text-slate-900 bg-slate-100"
                                    : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                            }`
                        }
                    >
                        Company Research
                    </NavLink>
                    <NavLink
                        to="/seller"
                        className={({ isActive }) =>
                            `px-3 py-1.5 text-sm transition-colors rounded-lg ${
                                isActive
                                    ? "font-medium text-slate-900 bg-slate-100"
                                    : "text-slate-500 hover:text-slate-700 hover:bg-slate-50"
                            }`
                        }
                    >
                        My Pitch
                    </NavLink>
                </nav>

                <div className="flex items-center gap-2">
                    <button
                        onClick={handleClearCache}
                        disabled={clearing}
                        title="Clear cache"
                        className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm text-white hover:bg-slate-50 hover:text-stone-900"
                    >
                        {clearing ? "Clearing…" : "Clear Cache"}
                    </button>
                    <div className="text-xs text-slate-500">v0.1</div>
                </div>
            </div>
        </header>
    );
}
