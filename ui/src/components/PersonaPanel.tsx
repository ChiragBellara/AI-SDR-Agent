import type { PersonaConent } from "../types/persona";

function Section({ title, children }: { title: string; children: React.ReactNode }) {
    return (
        <div className="rounded-xl border border-slate-200 p-5">
            <div className="mb-3 text-xs font-semibold uppercase tracking-widest text-slate-400">
                {title}
            </div>
            {children}
        </div>
    );
}

function Tag({ text }: { text: string }) {
    return (
        <span className="inline-block rounded-full bg-slate-100 px-2.5 py-0.5 text-xs text-slate-700">
            {text}
        </span>
    );
}

export default function PersonaPanel({ persona }: { persona: PersonaConent }) {
    return (
        <div className="flex h-full flex-col overflow-y-auto px-8 py-6">
        <div className="w-full">
            {/* Header */}
            <div className="mb-6">
                <div className="text-2xl font-semibold tracking-tight">{persona.company_name}</div>
                <div className="mt-1 flex flex-wrap gap-2 text-sm text-slate-500">
                    {persona.industry && <span>{persona.industry}</span>}
                    {persona.hq_location && (
                        <>
                            <span>·</span>
                            <span>{persona.hq_location}</span>
                        </>
                    )}
                </div>
                {persona.mission_statement && (
                    <p className="mt-3 text-sm text-slate-600 leading-relaxed">
                        {persona.mission_statement}
                    </p>
                )}
            </div>

            <div className="grid gap-4">
                {/* Core Products */}
                {persona.core_products?.length > 0 && (
                    <Section title="Core Products">
                        <div className="grid gap-3">
                            {persona.core_products.map((p, i) => (
                                <div key={i}>
                                    <div className="text-sm font-medium text-slate-900">{p.name}</div>
                                    <div className="mt-0.5 text-sm text-slate-500">{p.description}</div>
                                </div>
                            ))}
                        </div>
                    </Section>
                )}

                {/* Target Markets */}
                {persona.target_markets && (
                    <Section title="Target Markets">
                        {persona.target_markets.industries?.length > 0 && (
                            <div className="mb-3 flex flex-wrap gap-1.5">
                                {persona.target_markets.industries.map((ind, i) => (
                                    <Tag key={i} text={ind} />
                                ))}
                            </div>
                        )}
                        {persona.target_markets.ideal_customer_profile && (
                            <p className="text-sm text-slate-600">
                                {persona.target_markets.ideal_customer_profile}
                            </p>
                        )}
                    </Section>
                )}

                {/* Sales Triggers */}
                {persona.sales_triggers && (
                    <Section title="Sales Triggers">
                        {persona.sales_triggers.recent_funding_or_news && (
                            <div className="mb-3">
                                <div className="text-xs font-medium text-slate-500 mb-1">Recent News / Funding</div>
                                <p className="text-sm text-slate-700">{persona.sales_triggers.recent_funding_or_news}</p>
                            </div>
                        )}
                        {persona.sales_triggers.strategic_priorities && (
                            <div>
                                <div className="text-xs font-medium text-slate-500 mb-1">Strategic Priorities</div>
                                <p className="text-sm text-slate-700">{persona.sales_triggers.strategic_priorities}</p>
                            </div>
                        )}
                    </Section>
                )}

                {/* Impact Metrics */}
                {persona.impact_metrics?.length > 0 && (
                    <Section title="Impact Metrics">
                        <div className="grid gap-3">
                            {persona.impact_metrics.map((m, i) => (
                                <div key={i} className="flex gap-3">
                                    <div>
                                        <div className="text-sm text-slate-700">{m.case_study}</div>
                                        <div className="mt-0.5 text-sm font-medium text-slate-900">{m.result}</div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Section>
                )}

                {/* Sales Intelligence */}
                {persona.sales_intelligence && (
                    <Section title="Sales Intelligence">
                        {persona.sales_intelligence.green_flags?.length > 0 && (
                            <div className="mb-3">
                                <div className="text-xs font-medium text-slate-500 mb-1.5">Green Flags</div>
                                <div className="flex flex-wrap gap-1.5">
                                    {persona.sales_intelligence.green_flags.map((f, i) => (
                                        <span key={i} className="inline-block rounded-full bg-green-50 px-2.5 py-0.5 text-xs text-green-700">
                                            {f}
                                        </span>
                                    ))}
                                </div>
                            </div>
                        )}
                        {persona.sales_intelligence.red_flags && (
                            <div className="mb-3">
                                <div className="text-xs font-medium text-slate-500 mb-1">Red Flags</div>
                                <p className="text-sm text-slate-700">{persona.sales_intelligence.red_flags}</p>
                            </div>
                        )}
                        {persona.sales_intelligence.compliance_standards?.length > 0 && (
                            <div>
                                <div className="text-xs font-medium text-slate-500 mb-1.5">Compliance Standards</div>
                                <div className="flex flex-wrap gap-1.5">
                                    {persona.sales_intelligence.compliance_standards.map((s, i) => (
                                        <Tag key={i} text={s} />
                                    ))}
                                </div>
                            </div>
                        )}
                    </Section>
                )}
            </div>
        </div>
        </div>
    );
}
