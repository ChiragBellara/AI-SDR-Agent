export type Status = "queued" | "running" | "completed" | "failed";

export type ProfileJob = {
    job_id: string;
    status: Status;
    progress: { stage: string; percent: number; message: string };
    /* eslint-disable @typescript-eslint/no-explicit-any */
    result: any | null;
    error?: string | null;
};

const API_BASE = "http://localhost:8000";

export async function createProfile(input: {
    company_name: string;
    website_url: string;
    industry: string;
}): Promise<ProfileJob> {
    const res = await fetch(`${API_BASE}/profiles`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
    });
    if (!res.ok) throw new Error(`Failed to create profile (${res.status})`);
    return res.json();
}

export async function getProfile(jobId: string): Promise<ProfileJob> {
    const res = await fetch(`${API_BASE}/profiles/${jobId}`);
    if (!res.ok) throw new Error(`Failed to load job (${res.status})`);
    return res.json();
}
