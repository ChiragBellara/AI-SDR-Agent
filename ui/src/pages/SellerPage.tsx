import { useState } from "react";
import { Link } from "react-router-dom";
import Header from "../components/Header";
import Field from "../components/Field";
import { generateSellerBrief } from "../client";
import type {
    SellerBrief,
    FitAssessment,
    ObjectionMapEntry,
    OutreachTemplates,
} from "../types/persona";

// ---------------------------------------------------------------------------
// Clipboard copy button
// ---------------------------------------------------------------------------
function CopyButton({ text }: { text: string }) {
    const [copied, setCopied] = useState(false);

    async function handleCopy() {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    }

    return (
        <button
            onClick={handleCopy}
            className="ml-2 shrink-0 rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-500 hover:bg-slate-50 hover:text-slate-700 transition-colors"
        >
            {copied ? "Copied!" : "Copy"}
        </button>
    );
}

// ---------------------------------------------------------------------------
// Section wrapper
// ---------------------------------------------------------------------------
function Section({
    title,
    children,
}: {
    title: string;
    children: React.ReactNode;
}) {
    return (
        <div className="mb-6">
            <p className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
                {title}
            </p>
            {children}
        </div>
    );
}

// ---------------------------------------------------------------------------
// Fit Assessment card
// ---------------------------------------------------------------------------
const fitColors: Record<FitAssessment["fit_level"], string> = {
    Strong: "bg-emerald-50 border-emerald-200 text-emerald-800",
    Moderate: "bg-amber-50 border-amber-200 text-amber-800",
    Weak: "bg-red-50 border-red-200 text-red-700",
};

const fitBadgeColors: Record<FitAssessment["fit_level"], string> = {
    Strong: "bg-emerald-100 text-emerald-700",
    Moderate: "bg-amber-100 text-amber-700",
    Weak: "bg-red-100 text-red-700",
};

function FitAssessmentCard({
    fit,
    companyName,
}: {
    fit: FitAssessment;
    companyName: string;
}) {
    const isWeak = fit.fit_level === "Weak";
    return (
        <div className={`rounded-xl border p-4 ${fitColors[fit.fit_level]}`}>
            {isWeak && (
                <p className="mb-2 text-sm font-semibold">
                    This product is not a strong match for {companyName}
                </p>
            )}
            <div className="flex items-center gap-2 mb-3">
                <span
                    className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${fitBadgeColors[fit.fit_level]}`}
                >
                    {fit.fit_level} Fit
                </span>
            </div>
            <p className="text-sm">{fit.rationale}</p>
            {fit.strongest_connection && (
                <div className="mt-3 rounded-lg bg-white/60 px-3 py-2">
                    <p className="text-xs font-semibold uppercase tracking-wider mb-1 opacity-60">
                        {isWeak ? "Closest Overlap" : "Strongest Connection"}
                    </p>
                    <p className="text-sm">{fit.strongest_connection}</p>
                </div>
            )}
        </div>
    );
}

// ---------------------------------------------------------------------------
// Outreach Templates card
// ---------------------------------------------------------------------------
function OutreachTemplatesCard({
    templates,
    isWeak,
}: {
    templates: OutreachTemplates;
    isWeak: boolean;
}) {
    if (
        isWeak ||
        (!templates.email_subject &&
            !templates.email_opener &&
            !templates.call_opener)
    ) {
        return (
            <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-4 text-sm text-red-700">
                <p className="font-semibold mb-1">Not recommended</p>
                <p className="text-red-600">
                    Generating outreach for a weak fit risks damaging your
                    credibility. Address the fit gaps first — revisit this
                    account when their situation changes.
                </p>
            </div>
        );
    }

    const items: { label: string; value: string }[] = [];
    if (templates.email_subject)
        items.push({ label: "Email Subject", value: templates.email_subject });
    if (templates.email_opener)
        items.push({ label: "Email Opener", value: templates.email_opener });
    if (templates.call_opener)
        items.push({ label: "Call Opener", value: templates.call_opener });

    return (
        <div className="space-y-3">
            {items.map(({ label, value }) => (
                <div
                    key={label}
                    className="rounded-xl border border-slate-200 bg-white p-4"
                >
                    <div className="flex items-start justify-between gap-2">
                        <div className="flex-1">
                            <p className="mb-1.5 text-xs font-semibold uppercase tracking-wider text-slate-400">
                                {label}
                            </p>
                            <p className="text-sm text-slate-800 italic">
                                {value}
                            </p>
                        </div>
                        <CopyButton text={value} />
                    </div>
                </div>
            ))}
        </div>
    );
}

// ---------------------------------------------------------------------------
// Objection map card
// ---------------------------------------------------------------------------
function ObjectionCard({ entry }: { entry: ObjectionMapEntry }) {
    return (
        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-2.5">
            <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-0.5">
                    Risk
                </p>
                <p className="text-sm text-red-700">{entry.red_flag}</p>
            </div>
            <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-0.5">
                    How to Handle
                </p>
                <p className="text-sm text-slate-700">{entry.how_to_handle}</p>
            </div>
            <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-emerald-600 mb-0.5">
                    Reframe
                </p>
                <p className="text-sm font-medium text-slate-800 italic">
                    {entry.reframe}
                </p>
            </div>
        </div>
    );
}

// ---------------------------------------------------------------------------
// Brief output panel
// ---------------------------------------------------------------------------
function BriefPanel({
    brief,
    companyName,
}: {
    brief: SellerBrief;
    companyName: string;
}) {
    const isWeak = brief.fit_assessment.fit_level === "Weak";

    return (
        <div className="h-full overflow-y-auto px-8 py-6">
            <Section title="">
                <FitAssessmentCard
                    fit={brief.fit_assessment}
                    companyName={companyName}
                />
            </Section>

            {!isWeak && (
                <Section title="Lead With This">
                    <div className="rounded-xl border border-slate-200 bg-white p-4">
                        <p className="text-base font-semibold text-slate-900 mb-2">
                            {brief.lead_angle.entry_point}
                        </p>
                        <p className="text-sm text-slate-600">
                            {brief.lead_angle.why_this_first}
                        </p>
                    </div>
                </Section>
            )}

            {!isWeak && (
                <Section title="How to Position It">
                    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4 space-y-3">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-0.5">
                                Frame
                            </p>
                            <p className="text-sm text-slate-700">
                                {brief.positioning.frame}
                            </p>
                        </div>
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-0.5">
                                Against Their Priorities
                            </p>
                            <p className="text-sm text-slate-700">
                                {brief.positioning.against_priorities}
                            </p>
                        </div>
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-0.5">
                                Lead Differentiator
                            </p>
                            <p className="text-sm font-medium text-slate-900">
                                {brief.positioning.differentiator_to_lead_with}
                            </p>
                        </div>
                    </div>
                </Section>
            )}

            {brief.objection_map.length > 0 && (
                <Section title="Objection Map">
                    <div className="space-y-3">
                        {brief.objection_map.map((entry, i) => (
                            <ObjectionCard key={i} entry={entry} />
                        ))}
                    </div>
                </Section>
            )}

            <Section title="Outreach Templates">
                <OutreachTemplatesCard
                    templates={brief.outreach_templates}
                    isWeak={isWeak}
                />
            </Section>
        </div>
    );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------
type FormState = {
    product_name: string;
    product_description: string;
    target_industries: string;
    differentiators: string;
};

export default function SellerPage() {
    const lastPersonaRaw = localStorage.getItem("last_persona");
    const lastCompany = localStorage.getItem("last_persona_company") ?? null;
    const lastPersona = lastPersonaRaw ? JSON.parse(lastPersonaRaw) : null;

    const [form, setForm] = useState<FormState>({
        product_name: "",
        product_description: "",
        target_industries: "",
        differentiators: "",
    });
    const [brief, setBrief] = useState<SellerBrief | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    function set<K extends keyof FormState>(key: K, value: FormState[K]) {
        setForm((prev) => ({ ...prev, [key]: value }));
    }

    const canSubmit =
        form.product_name.trim().length > 0 &&
        form.product_description.trim().length > 0 &&
        !!lastPersona;

    async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
        e.preventDefault();
        if (!lastPersona) return;
        setLoading(true);
        setError(null);
        setBrief(null);
        try {
            const result = await generateSellerBrief({
                product_name: form.product_name,
                product_description: form.product_description,
                target_industries: form.target_industries || undefined,
                differentiators: form.differentiators || undefined,
                company_persona: lastPersona,
            });
            setBrief(result);
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
                    <div className="flex w-full flex-col justify-center px-10 py-8 md:w-80 md:shrink-0 md:border-r md:border-slate-200 overflow-y-auto">
                        <h1 className="text-2xl font-semibold tracking-tight">
                            My Pitch
                        </h1>
                        <p className="mt-2 text-sm text-slate-500">
                            Enter your product details to get tailored outreach
                            guidance for the researched company.
                        </p>

                        {/* Company context pill */}
                        <div className="mt-4">
                            {lastCompany ? (
                                <div className="inline-flex items-center gap-1.5 rounded-full bg-slate-100 px-3 py-1.5 text-xs text-slate-600">
                                    <svg
                                        className="h-3.5 w-3.5 text-slate-400"
                                        viewBox="0 0 16 16"
                                        fill="currentColor"
                                    >
                                        <path d="M8 1a7 7 0 100 14A7 7 0 008 1zm.75 4a.75.75 0 00-1.5 0v3.25l-1.5 1.5a.75.75 0 001.06 1.06l1.94-1.94V5z" />
                                    </svg>
                                    Researched:{" "}
                                    <span className="font-semibold text-slate-800">
                                        {lastCompany}
                                    </span>
                                </div>
                            ) : (
                                <div className="rounded-lg border border-amber-200 bg-amber-50 px-3 py-2 text-xs text-amber-700">
                                    No company researched yet.{" "}
                                    <Link
                                        to="/"
                                        className="font-medium underline"
                                    >
                                        Research a company first
                                    </Link>
                                    .
                                </div>
                            )}
                        </div>

                        <form onSubmit={onSubmit} className="mt-6 grid gap-4">
                            {/* Product Name */}
                            <Field
                                label="Product Name"
                                placeholder="e.g., Snowflake CRM"
                                value={form.product_name}
                                required={true}
                                onChange={(v) => set("product_name", v)}
                            />

                            {/* Product Description */}
                            <Field
                                label="Product Description"
                                placeholder="What does your product do and what problem does it solve?"
                                value={form.product_description}
                                required={true}
                                multiline={true}
                                rows={6}
                                onChange={(v) => set("product_description", v)}
                            />

                            {/* Target Industries */}
                            <Field
                                label="Target Industries"
                                placeholder="e.g., SaaS, FinTech, Healthcare, etc."
                                value={form.target_industries}
                                multiline={true}
                                rows={2}
                                onChange={(v) => set("target_industries", v)}
                            />

                            {/* Differentiators */}
                            <Field
                                label="Key Differentiators"
                                placeholder="What makes your product different from alternatives?"
                                value={form.differentiators}
                                multiline={true}
                                rows={2}
                                onChange={(v) => set("differentiators", v)}
                            />

                            {error && (
                                <p className="text-xs text-red-500">{error}</p>
                            )}

                            <div className="mt-1">
                                <button
                                    type="submit"
                                    disabled={!canSubmit || loading}
                                    className="inline-flex items-center justify-center rounded-xl bg-slate-900 px-4 py-2.5 text-sm font-medium text-white hover:bg-slate-50 hover:text-stone-900 disabled:cursor-not-allowed disabled:opacity-60 w-full"
                                >
                                    {loading
                                        ? "Generating…"
                                        : "Generate Pitch Brief"}
                                </button>
                            </div>
                        </form>
                    </div>

                    {/* Right: Output */}
                    <div className="hidden flex-1 overflow-hidden md:flex md:flex-col">
                        {brief ? (
                            <BriefPanel
                                brief={brief}
                                companyName={lastCompany ?? "this company"}
                            />
                        ) : loading ? (
                            <div className="flex h-full flex-col items-center justify-center gap-3 text-sm text-slate-500">
                                <svg
                                    className="h-5 w-5 animate-spin text-slate-400"
                                    viewBox="0 0 24 24"
                                    fill="none"
                                >
                                    <circle
                                        className="opacity-25"
                                        cx="12"
                                        cy="12"
                                        r="10"
                                        stroke="currentColor"
                                        strokeWidth="4"
                                    />
                                    <path
                                        className="opacity-75"
                                        fill="currentColor"
                                        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
                                    />
                                </svg>
                                Generating your pitch brief…
                            </div>
                        ) : (
                            <div className="flex h-full items-center justify-center">
                                <div className="text-center text-sm text-slate-400">
                                    Fill in your product details to generate a
                                    tailored pitch brief for {lastCompany}.
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
