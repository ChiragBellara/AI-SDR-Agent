import { useMemo, useState } from "react";
import Header from "./Header";
import Field from "./Field";
import PersonaPanel from "./PersonaPanel";
import { researchCompany } from "../client";
import type { PersonaConent } from "../types/persona";

type FormState = {
    company: string;
    url: string;
    industry: string;
};

const MOCK_PERSONA: PersonaConent = {
    company_name: "Glean",
    industry: "Enterprise AI",
    hq_location: "Palo Alto, CA",
    mission_statement: "Glean makes enterprise knowledge accessible by connecting all company apps and using AI to surface the right information at the right time.",
    core_products: [
        { name: "Glean Search", description: "Unified workplace search across 100+ apps including Slack, Jira, Drive, and Confluence." },
        { name: "Glean Assistant", description: "AI assistant trained on your company's knowledge to answer questions and draft content." },
        { name: "Glean Agents", description: "No-code AI agents that automate multi-step workflows across enterprise tools." },
    ],
    target_markets: {
        industries: ["Technology", "Financial Services", "Healthcare", "Retail", "Manufacturing"],
        ideal_customer_profile: "Mid-to-large enterprises (500+ employees) with fragmented knowledge across many SaaS tools, struggling with employee productivity and information overload.",
    },
    sales_triggers: {
        recent_funding_or_news: "Raised $260M Series F at a $4.6B valuation in 2024. Expanding aggressively into AI agents and international markets.",
        strategic_priorities: "Scaling enterprise sales motion, growing partner ecosystem, and deepening LLM integrations with proprietary company data.",
    },
    impact_metrics: [
        { case_study: "Global logistics firm with 12,000 employees", result: "40% reduction in time spent searching for information." },
        { case_study: "Fortune 500 financial services company", result: "Onboarding time cut by 30% using Glean Assistant for new hire Q&A." },
    ],
    sales_intelligence: {
        green_flags: ["Active hiring in AI/ML", "Recent funding round", "C-suite AI mandate", "High SaaS sprawl"],
        red_flags: "May face internal resistance from IT if existing intranet or search tools are recently purchased.",
        compliance_standards: ["SOC 2 Type II", "GDPR", "HIPAA Ready", "ISO 27001"],
    },
};

export default function Home() {
    const [form, setForm] = useState<FormState>({ company: "", url: "", industry: "" });
    const [persona, setPersona] = useState<PersonaConent | null>(MOCK_PERSONA);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const canSubmit = useMemo(() => {
        return form.company.trim().length > 0 && form.url.trim().length > 0;
    }, [form.company, form.url]);

    function set<K extends keyof FormState>(key: K, value: FormState[K]) {
        setForm((prev) => ({ ...prev, [key]: value }));
    }

    function fillExample() {
        setForm({ company: "Glean", url: "https://www.glean.com/", industry: "Enterprise AI" });
    }

    async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const result = await researchCompany({ company: form.company, company_url: form.url, industry: form.industry });
            setPersona(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Something went wrong");
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
                    <h1 className="text-2xl font-semibold tracking-tight">Company Researcher</h1>
                    <p className="mt-2 text-sm text-slate-500">
                        Enter a target company to generate a structured sales persona.
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

                        {error && (
                            <p className="text-xs text-red-500">{error}</p>
                        )}

                        <div className="mt-1 flex items-center gap-3">
                            <button
                                type="submit"
                                disabled={!canSubmit || loading}
                                className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-50 hover:text-stone-900 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {loading ? "Researching…" : "Start Research"}
                            </button>
                            <button
                                type="button"
                                onClick={fillExample}
                                className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-50 hover:text-stone-900"
                            >
                                Try example
                            </button>
                        </div>
                    </form>
                </div>

                {/* Right: Persona or empty state */}
                <div className="hidden flex-1 overflow-hidden md:flex md:flex-col">
                    {persona ? (
                        <PersonaPanel persona={persona} />
                    ) : (
                        <div className="flex h-full items-center justify-center">
                            <div className="text-center text-sm text-slate-400">
                                {loading
                                    ? "Running research workflow…"
                                    : "Results will appear here after you run a search."}
                            </div>
                        </div>
                    )}
                </div>
                </div>
            </div>
        </div>
    );
}
