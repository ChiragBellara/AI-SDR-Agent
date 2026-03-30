import type { PersonaConent } from "./types/persona";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export type ProgressEvent =
    | { type: "progress"; step: string; message: string }
    | { type: "node_done"; node: string; message: string }
    | { type: "done"; persona: PersonaConent }
    | { type: "error"; message: string };

export async function researchCompany(
    input: {
        company: string;
        company_url: string;
        industry: string;
        hq_location: string;
    },
    onEvent: (event: ProgressEvent) => void,
): Promise<PersonaConent> {
    // Step 1: kick off the job
    const res = await fetch(`${API_BASE}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
    });

    if (!res.ok) {
        throw new Error(`Failed to start research (${res.status})`);
    }

    const { job_id } = await res.json();

    // Step 2: consume the SSE stream
    return new Promise((resolve, reject) => {
        const es = new EventSource(`${API_BASE}/research/${job_id}/stream`);

        es.onmessage = (e) => {
            const event: ProgressEvent = JSON.parse(e.data);
            onEvent(event);

            if (event.type === "done") {
                es.close();
                resolve(event.persona);
            } else if (event.type === "error") {
                es.close();
                reject(new Error(event.message));
            }
        };

        es.onerror = () => {
            es.close();
            reject(new Error("Connection to research stream lost"));
        };
    });
}
