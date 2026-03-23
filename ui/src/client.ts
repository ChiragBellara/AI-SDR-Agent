import type { PersonaConent } from "./types/persona";

const API_BASE = import.meta.env.VITE_API_BASE_URL;

export async function researchCompany(input: {
    company: string;
    company_url: string;
    industry: string;
    hq_location: string;
}): Promise<PersonaConent> {
    const res = await fetch(`${API_BASE}/research`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
    });

    if (!res.ok) {
        throw new Error(`Failed to create profile (${res.status})`);
    }
    const data = await res.json();
    return data;
}
