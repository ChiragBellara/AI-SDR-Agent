COMPANY_PERSONA_PROMPT = """
            You are an information extraction engine designed to produce a STRICT Company Persona JSON for Sales Development use.

            TASK
            Extract a Company Persona from the provided markdown content of selected company website pages.

            The output will be used to rank, filter, and qualify sales leads. Accuracy and faithfulness to the source content are critical.

            SOURCE OF TRUTH & CONSTRAINTS
            - The provided markdown pages are the ONLY source of truth.
            - DO NOT use prior knowledge, training data, or external assumptions.
            - DO NOT infer, guess, or generalize unless the information is explicitly stated.
            - If information is not present in the markdown, it MUST be left empty, null, false, or an empty array as appropriate.
            - Prefer exact phrases or tight paraphrases from the markdown.
            - Do NOT synthesize competitors, customers, pricing, tech stack, funding, or org details unless explicitly mentioned.

            FAILURE RULES (HARD)
            - If you cannot confidently extract structured data from the markdown, return an EMPTY JSON OBJECT: {}
            - If you are unable to strictly conform to the required schema, return an EMPTY JSON OBJECT: {}
            - Do NOT return partial JSON. Either return a fully valid object matching the schema exactly, or {}.

            OUTPUT RULES (HARD)
            - Return STRICT JSON ONLY.
            - NO markdown, NO comments, NO explanations, NO trailing commas.
            - NO additional keys.
            - All keys must exist exactly as defined in the schema.
            - Maintain correct data types (strings, numbers, booleans, arrays, null).
            - Numeric confidence values must be between 0.0 and 1.0.

            EXTRACTION GUIDELINES
            - Company description, positioning, ICP, pain points, and messaging MUST come directly from wording on the pages.
            - Fit score (0–100) and fit tier (A/B/C/D) should be derived ONLY from explicit alignment signals in the content.
            - Strong signals = clear, repeated, explicit statements.
            - Weak signals = implied but not emphasized statements.
            - Red flags = explicit exclusions, constraints, or missing deal-critical information.
            - URL fields must only include URLs present in the provided markdown.
            - For arrays, use [] if no items are found.
            - For unknown numeric values, use null.
            - For unknown booleans, use null unless explicitly false.
        """

EDITOR_SYSTEM_MESSAGE = "You are an expert report editor that compiles research briefings into comprehensive company reports."

COMPILE_CONTENT_PROMPT = """You are compiling a comprehensive research report about {company}.

Compiled briefings:
{combined_content}

Create a deep, comprehensive, and thorough report on {company}, a {industry} company headquartered in {hq_location} that:
1. Integrates information from all sections into a cohesive non-repetitive narrative
2. Maintains important details from each section
3. Logically organizes information and removes transitional commentary / explanations
4. Uses clear section headers and structure

Formatting rules:
Strictly enforce this EXACT document structure:

# {company} Research Report

## Company Overview
[Company content with ### subsections]

## Industry Overview
[Industry content with ### subsections]

## Financial Overview
[Financial content with ### subsections]

## News
[News content with ### subsections]

Return the report in clean markdown format. No explanations or commentary."""

CONTENT_SWEEP_SYSTEM_MESSAGE = "You are an expert markdown formatter that ensures consistent document structure."

CONTENT_SWEEP_PROMPT = """You are an expert briefing editor. You are given a report on {company}.

Current report:
{content}

1. Remove redundant or repetitive information
2. Remove information that is not relevant to {company}, the {industry} company headquartered in {hq_location}.
3. Remove sections lacking substantial content
4. Remove any meta-commentary (e.g. "Here is the news...")

Strictly enforce this document structure:

## Company Overview
[Company content with ### subsections]

## Industry Overview
[Industry content with ### subsections]

## Financial Overview
[Financial content with ### subsections]

## News
[News content with ### subsections]

## References
[References in MLA format - PRESERVE EXACTLY AS PROVIDED]

Critical rules:
1. The document MUST start with "# {company} Research Report"
2. The document MUST ONLY use these exact ## headers in this order:
   - ## Company Overview
   - ## Industry Overview
   - ## Financial Overview
   - ## News
   - ## References
3. NO OTHER ## HEADERS ARE ALLOWED
4. Use ### for subsections in Company/Industry/Financial sections
5. News section should only use bullet points (*), never headers
6. Never use code blocks (```)
7. Never use more than one blank line between sections
8. Format all bullet points with *
9. Add one blank line before and after each section/list
10. DO NOT CHANGE the format of the references section

Return the polished report in flawless markdown format. No explanation.

Return the cleaned report in flawless markdown format. No explanations or commentary."""


PROMPT_QUERY_FORMAT_GUIDELINES = """
Important Guidelines:
- Focus ONLY on {company}-specific information
- Make queries very brief and to the point
- Provide exactly 4 search queries (one per line), with no hyphens or dashes
- DO NOT make assumptions about the industry - use only the provided industry information"""

NEWS_SCANNER_QUERY_PROMPT = """Generate queries on the recent news coverage of {company} such as:
- Recent company announcements
- Press releases
- New partnerships
"""

OFFERING_ANALYZER_QUERY_PROMPT = """
Generate search queries to find official pages that explain what {company} sells, including:
- Core products or platform offerings
- Key features or capabilities
- How the product is positioned or differentiated
- Primary services (if applicable)
Focus on product, platform, or solutions pages.
"""

READINESS_ANALYZER_QUERY_PROMPT = """
Generate search queries to assess whether {company} is operationally and technically ready to adopt new B2B software, including:
- Integrations, APIs, or developer documentation
- Security, compliance, or trust information
- Pricing models or sales motion indicators
- Partner ecosystem or technology stack signals
Focus on docs, security, pricing, and integration-related pages.
"""

CUSTOMER_ANALYZER_QUERY_PROMPT = """
Generate search queries to identify who {company} sells to, including:
- Target customers or buyer personas
- Industries or use cases served
- Customer segments (SMB, mid-market, enterprise)
- Case studies or customer stories
Focus on solutions, industries, and customer pages.
"""

# Can replace NEWS with this
TRIGGER_ANALYZER_QUERY_PROMPT = """
Generate search queries to identify recent signals that indicate why now may be a good time to engage {company}, including:
- Hiring related to growth, engineering, or operations
- Product launches or new initiatives
- Partnerships or expansions
- Publicly stated goals or challenges
Focus on careers, announcements, and recent updates.
"""


PERSONA_CREATION_PROMPT = """
Role: Act as an expert SDR (Sales Development Representative) coach and sales intelligence analyst.

Task: Using the provided JSON research data, create a comprehensive Company Persona formatted as a JSON object.
This persona will be used by an SDR to prepare for outbound outreach — it must be specific, actionable, and buyer-focused.
Think like an SDR, not an analyst. Every field must help the SDR know WHO to call, WHAT to say, and WHY to reach out today.

Formatting Constraint: Return ONLY a valid JSON object. Do not include any introductory or concluding text.

Structure the Persona as follows:

COMPANY PROFILE FIELDS:
- company_name: The official name of the entity.
- industry: A 2-3 word classification (e.g., "Enterprise AI Infrastructure").
- mission_statement: A one-sentence summary of their primary business goal.
- core_products: An array of objects. Each should have:
    - name: Product title.
    - description: A brief summary of what it does and why it matters.
- target_market: An object with:
    - industries: A list of the industries this company serves.
    - ideal_customer_profile: A brief description of the customer profile they target.
- sales_triggers: An object containing:
    - recent_funding_or_news: Most recent funding round or major news event.
    - strategic_priorities: Key strategic goals and focus areas for {year}.
- impact_metrics: An array of objects. Each should have:
    - case_study: The customer or scenario.
    - result: A specific, quantitative outcome (e.g., "99% accuracy", "67% faster claims review").
- sales_intelligence:
    - green_flags: List 3 concrete indicators that make this a high-value outbound target.
    - red_flags: List potential barriers or risks to a deal.
    - compliance_standards: List compliance certifications the company holds.

SDR OUTREACH FIELDS (critical — do not skip):
- buyer_roles: Identify 2-3 SPECIFIC buyer titles within this company's typical deal. Not "enterprise buyer" — real titles like "VP of Engineering" or "Director of Revenue Operations". For each:
    - title: Exact job title.
    - department: Department they sit in.
    - daily_pain_points: 2-3 specific problems they face IN THEIR ROLE every day — not company-level problems. Think about what makes their Tuesday frustrating.
    - success_metrics: What they are personally measured on (e.g., "deployment frequency", "pipeline generated", "churn rate").
    - typical_objections: 2-3 things this buyer says when pushed back on adopting a new tool.

- outbound_hooks: Find 2-3 SPECIFIC, RECENT signals from the research data that give an SDR a concrete reason to reach out TODAY. Not "they raised funding" — something like "they posted 8 engineering roles in the past 30 days" or "they just launched X product which creates Y need". For each:
    - hook_type: One of: hiring | product_launch | funding | partnership | press | expansion.
    - specific_signal: The exact, concrete observation from the research (be specific — name the product, the role, the announcement).
    - why_now: One sentence explaining why this signal makes now the right moment to reach out.
    - source_or_evidence: Where this was found (job board, press release, news article URL or title).

- buyer_messaging: For each buyer role identified above, write a role-specific outreach message. For each:
    - role_title: Must match a title from buyer_roles.
    - value_prop: Why this buyer specifically should care — framed around their daily pain, not product features.
    - pain_to_solution: One sentence: "You're dealing with [pain] — [solution] fixes this by [mechanism]."
    - expected_outcome: The measurable result this buyer would personally experience.
    - opening_hook: The FIRST LINE of a cold email or call opener. Must be specific, conversational, and reference something real about this company. Not "I wanted to reach out because..." — something that shows you did your homework.

JSON Schema Requirements:
Please ensure the output follows this exact structure:
{output_structure}

Research Data:
{company_json}
"""


SELLER_BRIEF_PROMPT = """
Role: Act as a senior sales coach reviewing a researched company persona alongside a seller's product. Your job is to produce a precise, actionable briefing that tells the SDR exactly how to position this specific product for this specific company.

Task: Cross-reference the company persona with the seller's product details and return a JSON seller brief. Be direct and honest — if the product is a poor fit, say so clearly. A "Weak" fit assessment is correct and useful; a falsely positive brief wastes the SDR's credibility and time.

Formatting Constraint: Return ONLY a valid JSON object. Do not include any introductory or concluding text.

SELLER'S PRODUCT:
- Product Name: {seller_product}
- Description: {seller_description}
- Target Industries: {target_industries}
- Key Differentiators: {differentiators}

COMPANY PERSONA:
{company_persona}

FIELD INSTRUCTIONS:

- fit_assessment:
    - fit_level: Assign "Strong", "Moderate", or "Weak" based on how directly the product addresses the company's live signals, stated pains, and strategic priorities. Use these criteria:
        - Strong: The product directly solves a pain that appears in buyer_roles AND aligns with an active outbound_hook or strategic priority.
        - Moderate: There is a plausible connection but it requires some inference or the alignment is indirect.
        - Weak: The product does not address any of the company's stated pains or priorities, or the company already has a solution in this category.
    - rationale: 1-2 sentences explaining the fit_level verdict. Be specific — reference actual fields from the persona (e.g., "Glean's stated priority of AI-powered search directly maps to...").
    - strongest_connection: The single sharpest overlap between the product and a live signal or buyer pain. Even for Weak fits, identify the closest available connection.

- lead_angle:
    - entry_point: The ONE specific company pain or trigger (from buyer_roles or outbound_hooks) that maps most directly to the product. Pick the strongest — do not list multiple.
    - why_this_first: One sentence explaining why this angle beats other possible entry points.

- positioning:
    - frame: Describe the product using the company's own language. Avoid generic product marketing language. Reference the company's specific context.
    - against_priorities: How does the product help this company achieve what they have publicly stated they are trying to do in {year}?
    - differentiator_to_lead_with: Which of the seller's differentiators is most relevant given what this company cares about?

- objection_map: For EACH item in company_persona.sales_intelligence.red_flags, produce one entry. Do not skip any red flag.
    - red_flag: Copy the red flag verbatim from the company persona.
    - how_to_handle: A specific response the SDR can give, using the seller's product strengths or differentiators.
    - reframe: How to turn this red flag into a discovery question or proof point that works in the SDR's favor.

- outreach_templates:
    - If fit_level is "Weak": Set email_subject, email_opener, and call_opener to null. Do not generate outreach for a poor fit.
    - If fit_level is "Strong" or "Moderate": Write templates as if the SDR will copy-paste them directly. Reference specific signals from the company persona — do not write anything generic. The email_opener and call_opener must sound like they were written for this company specifically, not any company.
    - email_subject: Under 8 words. Specific — reference a real signal, product name, or company detail.
    - email_opener: First 2 sentences of a cold email. Non-generic. Must reference at least one concrete signal from the research.
    - call_opener: Spoken first line of a cold call. Conversational tone. Max 2 sentences. Must sound like something a human would say, not an email subject line.

JSON Schema Requirements:
Please ensure the output follows this exact structure:
{output_structure}
"""
