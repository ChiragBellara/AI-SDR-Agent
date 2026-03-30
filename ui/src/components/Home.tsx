import { useMemo, useState } from "react";
import Header from "./Header";
import Field from "./Field";
import PersonaPanel from "./PersonaPanel";
import ProgressPanel from "./ProgressPanel";
import { researchCompany, type ProgressEvent } from "../client";
import type { PersonaConent } from "../types/persona";

type FormState = {
    company: string;
    url: string;
    industry: string;
    hq_location: string;
};

export default function Home() {
    const [form, setForm] = useState<FormState>({
        company: "",
        url: "",
        industry: "",
        hq_location: "",
    });
    const [persona, setPersona] = useState<PersonaConent | null>();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [steps, setSteps] = useState<
        { node: string; message: string; done: boolean }[]
    >([]);

    const canSubmit = useMemo(() => {
        return form.company.trim().length > 0 && form.url.trim().length > 0;
    }, [form.company, form.url]);

    function set<K extends keyof FormState>(key: K, value: FormState[K]) {
        setForm((prev) => ({ ...prev, [key]: value }));
    }

    function fillExample() {
        setForm({
            company: "Glean",
            url: "https://www.glean.com/",
            industry: "Enterprise AI",
            hq_location: "San Francisco, CA",
        });
    }

    async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setPersona(null);
        setSteps([]);
        try {
            const result = await researchCompany(
                {
                    company: form.company,
                    company_url: form.url,
                    industry: form.industry,
                    hq_location: form.hq_location,
                },
                (event: ProgressEvent) => {
                    if (event.type === "node_done") {
                        setSteps((prev) => [
                            ...prev,
                            {
                                node: event.node,
                                message: event.message,
                                done: true,
                            },
                        ]);
                    }
                },
            );
            setPersona(result);
        } catch (err) {
            setError(
                err instanceof Error ? err.message : "Something went wrong",
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="flex h-screen flex-col overflow-hidden bg-white text-slate-900">
            <Header />

            <div className="flex flex-1 justify-center overflow-hidden">
                <div className="flex w-full max-w-5xl overflow-hidden">
                    {/* Left: Form */}
                    <div className="flex w-full flex-col justify-center px-10 py-8 md:w-80 md:shrink-0 md:border-r md:border-slate-200">
                        <h1 className="text-2xl font-semibold tracking-tight">
                            Company Researcher
                        </h1>
                        <p className="mt-2 text-sm text-slate-500">
                            Enter a target company to generate a structured
                            sales persona.
                        </p>

                        <form onSubmit={onSubmit} className="mt-6 grid gap-4">
                            <Field
                                label="Company Name"
                                placeholder="e.g., Snowflake"
                                value={form.company}
                                onChange={(v) => set("company", v)}
                            />
                            <Field
                                label="Company URL"
                                placeholder="https://example.com"
                                value={form.url}
                                onChange={(v) => set("url", v)}
                            />
                            <Field
                                label="Industry"
                                placeholder="e.g., Data Infrastructure"
                                value={form.industry}
                                onChange={(v) => set("industry", v)}
                            />

                            <Field
                                label="HQ"
                                placeholder="e.g., San Francisco, CA"
                                value={form.hq_location}
                                onChange={(v) => set("hq_location", v)}
                            />

                            {error && (
                                <p className="text-xs text-red-500">{error}</p>
                            )}

                            <div className="mt-1 flex items-center gap-3">
                                <button
                                    type="submit"
                                    disabled={!canSubmit || loading}
                                    className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-50 hover:text-stone-900 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    {loading
                                        ? "Researching…"
                                        : "Start Research"}
                                </button>
                                <button
                                    type="button"
                                    disabled={loading}
                                    onClick={fillExample}
                                    className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-50 hover:text-stone-900 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    Try example
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Right: Persona / Progress / empty state */}
                    <div className="hidden flex-1 overflow-hidden md:flex md:flex-col">
                        {persona ? (
                            <PersonaPanel persona={persona} />
                        ) : loading ? (
                            <ProgressPanel
                                completedSteps={steps}
                                company={form.company}
                            />
                        ) : (
                            <div className="flex h-full items-center justify-center">
                                <div className="text-center text-sm text-slate-400">
                                    Results will appear here after you run a
                                    search.
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
