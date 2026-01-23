# AI-SDR-Agent

### Project Overview
A tool that takes a company URL, scrapes their latest news/blog, finds a relevant lead on LinkedIn (simulated or via API), and generates a hyper-personalized, multi-channel outreach strategy.

### Key Features
- **Schema-strict extraction using Pydantic** to enforce consistent, typed JSON outputs and catch malformed fields early.
- **Noise-reduced markdown crawling** to remove navigation, boilerplate, and irrelevant content.
- **Pluggable LLM** backends (OpenAI / Groq) for flexible cost–latency tradeoffs.
- Deterministic validation and post-processing for reliable downstream automation.

### Technical Stack
- Crawl4AI (crawling + content-to-markdown)
- Pydantic (schema validation + strict structured outputs)
- OpenAI / Anthropic (LLM-based structured extraction)
- UV (fast Python env + dependency management)

### Architecture
The system separates the Scraper from the Processor to decouple ingestion from extraction logic. This makes crawling independently testable/retryable (network + site variability) while keeping the processor focused on schema enforcement, LLM prompting, and post-validation so you can swap crawlers, run batch jobs, or re-process cached markdown without re-scraping.

### Sample Output
```json
[
    {
        "name": "Anthropic",
        "value_proposition": "AI will have a vast impact on the world. Anthropic is a public benefit corporation dedicated to securing its benefits and mitigating its risks.",
        "target_icp": [
            "Businesses seeking AI solutions",
            "Developers looking for AI tools",
            "Organizations focused on responsible AI development"
        ],
        "tech_stack_hints": [
            "Claude Developer Platform",
            "AI models like Claude, Opus, Sonnet, Haiku",
            "Integration with platforms like Amazon Bedrock and Google Cloud’s Vertex AI"
        ],
        "error": false
    }
]
```
