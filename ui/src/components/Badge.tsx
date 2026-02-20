import type { BadgeKind } from "../types";

export function Badge(props: { kind: BadgeKind; children: React.ReactNode }) {
    const cls =
        props.kind === "good"
            ? "badge good"
            : props.kind === "warn"
            ? "badge warn"
            : props.kind === "bad"
            ? "badge bad"
            : "badge";
    return <span className={cls}>{props.children}</span>;
}