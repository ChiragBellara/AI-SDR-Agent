import type { PersonaConent, BuyerRole, OutboundHook, BuyerMessaging } from "../types/persona";

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

function Badge({ text, color = "slate" }: { text: string; color?: "slate" | "emerald" | "amber" | "blue" | "violet" }) {
    const colors = {
        slate:   "bg-slate-100 text-slate-700",
        emerald: "bg-emerald-50 text-emerald-700",
        amber:   "bg-amber-50 text-amber-700",
        blue:    "bg-blue-50 text-blue-700",
        violet:  "bg-violet-50 text-violet-700",
    };
    return (
        <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${colors[color]}`}>
            {text}
        </span>
    );
}

const HOOK_COLORS: Record<string, "emerald" | "amber" | "blue" | "violet" | "slate"> = {
    hiring:          "emerald",
    product_launch:  "blue",
    funding:         "amber",
    partnership:     "violet",
    press:           "slate",
    expansion:       "blue",
};

function BuyerRoleCard({ role }: { role: BuyerRole }) {
    return (
        <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div className="flex items-center gap-2">
                <span className="text-sm font-semibold text-slate-900">{role.title}</span>
                {role.department && (
                    <Badge text={role.department} />
                )}
            </div>

            {role.daily_pain_points?.length > 0 && (
                <div className="mt-3">
                    <div className="mb-1 text-xs font-medium text-slate-500">Daily Pain Points</div>
                    <ul className="space-y-1">
                        {role.daily_pain_points.map((pain, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-red-400" />
                                {pain}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {role.success_metrics?.length > 0 && (
                <div className="mt-3">
                    <div className="mb-1 text-xs font-medium text-slate-500">Measured On</div>
                    <ul className="space-y-1">
                        {role.success_metrics.map((metric, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-400" />
                                {metric}
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {role.typical_objections?.length > 0 && (
                <div className="mt-3">
                    <div className="mb-1 text-xs font-medium text-slate-500">Typical Objections</div>
                    <ul className="space-y-1">
                        {role.typical_objections.map((obj, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-slate-600 italic">
                                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
                                "{obj}"
                            </li>
                        ))}
                    </ul>
                </div>
            )}
        </div>
    );
}

function HookCard({ hook }: { hook: OutboundHook }) {
    const color = HOOK_COLORS[hook.hook_type] ?? "slate";
    return (
        <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div className="mb-2 flex items-center gap-2">
                <Badge text={hook.hook_type.replace("_", " ")} color={color} />
            </div>
            <p className="text-sm font-medium text-slate-900">{hook.specific_signal}</p>
            {hook.why_now && (
                <p className="mt-1.5 text-sm text-slate-600">
                    <span className="font-medium text-slate-700">Why now: </span>
                    {hook.why_now}
                </p>
            )}
            {hook.source_or_evidence && (
                <p className="mt-1.5 text-xs text-slate-400">{hook.source_or_evidence}</p>
            )}
        </div>
    );
}

function MessagingCard({ msg }: { msg: BuyerMessaging }) {
    return (
        <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
            <div className="mb-3 text-sm font-semibold text-slate-900">{msg.role_title}</div>

            {msg.opening_hook && (
                <div className="mb-3 rounded-lg border border-slate-200 bg-white px-4 py-3">
                    <div className="mb-1.5 text-xs font-medium uppercase tracking-widest text-slate-400">
                        Opening Hook
                    </div>
                    <p className="text-sm italic text-slate-800">"{msg.opening_hook}"</p>
                </div>
            )}

            {msg.pain_to_solution && (
                <div className="mt-2">
                    <div className="mb-1 text-xs font-medium text-slate-500">Pain → Solution</div>
                    <p className="text-sm text-slate-700">{msg.pain_to_solution}</p>
                </div>
            )}

            {msg.value_prop && (
                <div className="mt-2">
                    <div className="mb-1 text-xs font-medium text-slate-500">Value Prop</div>
                    <p className="text-sm text-slate-700">{msg.value_prop}</p>
                </div>
            )}

            {msg.expected_outcome && (
                <div className="mt-2">
                    <div className="mb-1 text-xs font-medium text-slate-500">Expected Outcome</div>
                    <p className="text-sm font-medium text-emerald-700">{msg.expected_outcome}</p>
                </div>
            )}
        </div>
    );
}

export default function OutreachPanel({ persona }: { persona: PersonaConent }) {
    const { buyer_roles = [], outbound_hooks = [], buyer_messaging = [] } = persona;

    const isEmpty = buyer_roles.length === 0 && outbound_hooks.length === 0 && buyer_messaging.length === 0;

    if (isEmpty) {
        return (
            <div className="flex h-full items-center justify-center px-8">
                <p className="text-sm text-slate-400">No outreach intelligence available for this persona.</p>
            </div>
        );
    }

    return (
        <div className="flex h-full flex-col overflow-y-auto px-8 py-6">
            <div className="w-full space-y-4">

                {outbound_hooks.length > 0 && (
                    <Section title="Outbound Hooks — Why Reach Out Now">
                        <div className="space-y-3">
                            {outbound_hooks.map((hook, i) => (
                                <HookCard key={i} hook={hook} />
                            ))}
                        </div>
                    </Section>
                )}

                {buyer_roles.length > 0 && (
                    <Section title="Buyer Roles">
                        <div className="space-y-3">
                            {buyer_roles.map((role, i) => (
                                <BuyerRoleCard key={i} role={role} />
                            ))}
                        </div>
                    </Section>
                )}

                {buyer_messaging.length > 0 && (
                    <Section title="Messaging by Role">
                        <div className="space-y-3">
                            {buyer_messaging.map((msg, i) => (
                                <MessagingCard key={i} msg={msg} />
                            ))}
                        </div>
                    </Section>
                )}

            </div>
        </div>
    );
}
