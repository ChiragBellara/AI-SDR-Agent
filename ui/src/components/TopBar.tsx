
export function TopBar(props: { company: string; status: string; fit: number }) {
    return (
        <header>
            <div className="brand">
                <span className="dot" />
                <span>AI-SDR Agent</span>
            </div>

            <span className="pill">
                <strong>Company:</strong> {props.company}
            </span>
            <span className="pill">
                <strong>Status:</strong> {props.status}
            </span>
            <span className="pill">
                <strong>Fit:</strong> {props.fit.toFixed(1)}
            </span>

            <div className="spacer" />

            <button className="btn">Export JSON</button>
            <button className="btn">Clone Run</button>
            <button className="btn primary">New Run</button>
        </header>
    );
}