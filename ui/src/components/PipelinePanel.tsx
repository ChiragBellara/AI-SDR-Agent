import { Badge } from "./Badge";
import type { Step, Source } from "../types";
import { SourceItem } from "./SourceItem";
import { StepCard } from "./StepCard";

export function PipelinePanel(props: { steps: Step[]; sources: Source[] }) {
    return (
        <section className="panel">
        <div className="hd">
            <h3>Pipeline</h3>
            <Badge kind="warn">LIVE</Badge>
        </div>

        <div className="bd">
            {props.steps.map((s) => (
            <StepCard key={s.name} step={s} />
            ))}

            <div style={{ height: 10 }} />

            <div className="hd" style={{ border: "1px solid var(--border)", borderRadius: 14, marginTop: 12 }}>
            <h3>Sources</h3>
            <Badge kind="neutral">{props.sources.length}</Badge>
            </div>

            <div style={{ height: 10 }} />

            <div className="list">
            {props.sources.map((src) => (
                <SourceItem key={src.url} source={src} />
            ))}
            </div>
        </div>
        </section>
    );
    }