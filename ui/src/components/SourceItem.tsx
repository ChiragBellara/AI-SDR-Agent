import type { Source } from "../types";

export function SourceItem({ source }: { source: Source }) {
    return (
        <div className="source">
            <div className="url">{source.url}</div>
            <div className="snip">{source.snippet}</div>
        </div>
    );
}