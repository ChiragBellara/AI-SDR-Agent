import { useState } from "react";
import { useNavigate } from "react-router-dom";
import Card from "../components/Card";
import Input from "../components/Input";
import Button from "../components/Button";
import { createProfile } from "../client";

export default function NewProfilePage() {
    const nav = useNavigate();
    const [companyName, setCompanyName] = useState("");
    const [websiteUrl, setWebsiteUrl] = useState("");
    const [industry, setIndustry] = useState("");
    const [loading, setLoading] = useState(false);
    const [err, setErr] = useState<string | null>(null);

    async function onSubmit(e: React.FormEvent) {
        e.preventDefault();
        setErr(null);
        setLoading(true);
        try {
        const job = await createProfile({
            company_name: companyName.trim(),
            website_url: websiteUrl.trim(),
            industry: industry.trim(),
        });
        nav(`/run/${job.job_id}`);
        /* eslint-disable @typescript-eslint/no-explicit-any */
        } catch (e: any) {
        setErr(e?.message ?? "Something went wrong");
        } finally {
        setLoading(false);
        }
    }

    function fillExample() {
        setCompanyName("Snorkel AI");
        setWebsiteUrl("https://snorkel.ai");
        setIndustry("Enterprise AI");
    }

    return (
        <div className="grid gap-6">
        <div>
            <h1 className="text-3xl font-semibold tracking-tight">Generate a company profile</h1>
            <p className="mt-2 text-slate-600 max-w-2xl">
            Enter a company name, website, and industry. The system calls your FastAPI endpoint, runs the pipeline, and renders the
            resulting profile.
            </p>
        </div>

        <Card className="p-6">
            <form onSubmit={onSubmit} className="grid gap-4">
            <div className="grid gap-1">
                <label className="text-sm text-slate-700">Company name</label>
                <Input value={companyName} onChange={(e) => setCompanyName(e.target.value)} placeholder="e.g., Snowflake" />
            </div>

            <div className="grid gap-1">
                <label className="text-sm text-slate-700">Website URL</label>
                <Input value={websiteUrl} onChange={(e) => setWebsiteUrl(e.target.value)} placeholder="https://example.com" />
            </div>

            <div className="grid gap-1">
                <label className="text-sm text-slate-700">Industry</label>
                <Input value={industry} onChange={(e) => setIndustry(e.target.value)} placeholder="e.g., Data Infrastructure" />
            </div>

            {err && <div className="text-sm text-red-600">{err}</div>}

            <div className="flex items-center gap-2">
                <Button type="submit" disabled={loading || !companyName || !websiteUrl}>
                {loading ? "Starting..." : "Generate Profile"}
                </Button>
                <Button type="button" variant="ghost" onClick={fillExample}>
                Use Example
                </Button>
            </div>
            </form>
        </Card>

        <Card className="p-6">
            <div className="text-sm text-slate-700 font-medium">Next step</div>
            <p className="mt-2 text-sm text-slate-600">
            Replace the backend’s <span className="font-mono">fake_generate_profile()</span> with your LangGraph workflow output.
            Keep the same job contract so the UI stays stable.
            </p>
        </Card>
        </div>
    );
}