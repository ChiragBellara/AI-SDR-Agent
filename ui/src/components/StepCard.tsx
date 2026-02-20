import type { Step } from "../types";
import { Badge } from "./Badge";

export function StepCard({ step }: { step: Step }) {
    return (
        <div className="step">
        <div className="row">
            <strong>{step.name}</strong>
            <Badge kind={step.badge}>{step.status}</Badge>
        </div>
        <div className="meta">
            {step.chips.map((c) => (
            <span className="chip" key={c}>
                {c}
            </span>
            ))}
        </div>
        </div>
    );
}