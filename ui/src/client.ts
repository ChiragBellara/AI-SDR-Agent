import type { PersonaConent, SellerBrief } from "./types/persona";

const API_BASE = import.meta.env.VITE_API_BASE_URL;
const API_KEY = import.meta.env.VITE_API_KEY as string | undefined;

const POST_TIMEOUT_MS = 30_000; // 30 s to start the job
const STREAM_TIMEOUT_MS = 10 * 60_000; // 10 min max for the full research run

export type ProgressEvent =
    | { type: "progress"; step: string; message: string }
    | { type: "node_done"; node: string; message: string }
    | {
          type: "done";
          persona: PersonaConent;
          cache_hit?: boolean;
          cached_at?: string;
      }
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
    // Step 1: kick off the job (with timeout)
    const controller = new AbortController();
    const postTimer = setTimeout(() => controller.abort(), POST_TIMEOUT_MS);

    let job_id: string;
    try {
        const headers: Record<string, string> = {
            "Content-Type": "application/json",
        };
        if (API_KEY) headers["X-API-Key"] = API_KEY;

        const res = await fetch(`${API_BASE}/research`, {
            method: "POST",
            headers,
            body: JSON.stringify(input),
            signal: controller.signal,
        });

        if (!res.ok) {
            const body = await res.json().catch(() => ({}));
            throw new Error(
                body?.detail ?? `Failed to start research (${res.status})`,
            );
        }

        ({ job_id } = await res.json());
    } catch (err) {
        if ((err as Error).name === "AbortError") {
            throw new Error(
                "Request timed out. The server may be starting up — please try again.",
            );
        }
        throw err;
    } finally {
        clearTimeout(postTimer);
    }

    // Step 2: consume the SSE stream (with overall timeout)
    return new Promise((resolve, reject) => {
        const es = new EventSource(`${API_BASE}/research/${job_id}/stream`);

        const streamTimer = setTimeout(() => {
            es.close();
            reject(
                new Error(
                    "Research timed out after 10 minutes. Please try again.",
                ),
            );
        }, STREAM_TIMEOUT_MS);

        es.onmessage = (e) => {
            const event: ProgressEvent = JSON.parse(e.data);
            onEvent(event);

            if (event.type === "done") {
                clearTimeout(streamTimer);
                es.close();
                resolve(event.persona);
            } else if (event.type === "error") {
                clearTimeout(streamTimer);
                es.close();
                reject(new Error(event.message));
            }
        };

        es.onerror = () => {
            clearTimeout(streamTimer);
            es.close();
            reject(
                new Error(
                    "Connection to research stream lost. Please try again.",
                ),
            );
        };
    });
}

const SELLER_BRIEF_TIMEOUT_MS = 60_000; // 60 s — single LLM call

export async function generateSellerBrief(input: {
    product_name: string;
    product_description: string;
    target_industries?: string;
    differentiators?: string;
    company_persona: PersonaConent;
}): Promise<SellerBrief> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), SELLER_BRIEF_TIMEOUT_MS);

    try {
        const headers: Record<string, string> = {
            "Content-Type": "application/json",
        };
        if (API_KEY) headers["X-API-Key"] = API_KEY;

        const res = await fetch(`${API_BASE}/seller-brief`, {
            method: "POST",
            headers,
            body: JSON.stringify(input),
            signal: controller.signal,
        });

        if (!res.ok) {
            const body = await res.json().catch(() => ({}));
            throw new Error(
                body?.detail ??
                    `Failed to generate seller brief (${res.status})`,
            );
        }

        const { seller_brief } = await res.json();
        return seller_brief as SellerBrief;
    } catch (err) {
        if ((err as Error).name === "AbortError") {
            throw new Error("Request timed out. Please try again.");
        }
        throw err;
    } finally {
        clearTimeout(timer);
    }
}
