
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
        </header>
    );
}