CRAWL_INSTRUCTION = """
            You are an AI-SDR agent building a reusable company 'LeadCard' memory object.\n
            From the provided markdowns, populate the LeadCard schema with ONLY what is explicitly supported by the text.\n
            Do NOT guess or infer details that are not present unless it is explicitly allowed below. If a field is not supported, use an empty list or null.\n\n
            Guidelines:\n
            - company_name: exact company name as written.\n
            - category: short category (e.g., 'Fleet management', 'AI developer tools', 'Fintech'), only if clearly stated.\n
            - one_liner: 1 sentence describing what the company does.\n
            - products_or_platform: product names, platform modules, offerings mentioned.\n
            - target_customers: industries or customer types explicitly mentioned.\n
            - core_workflows: what users do with the product (e.g., 'monitor fleets', 'manage invoices', 'deploy agents').\n
            - technical_surface_area: APIs, SDKs, integrations, data pipelines, security/compliance features, admin controls—anything that implies technical complexity.\n
            - integrations_or_stack_hints: named tools, clouds, standards, integrations (e.g., 'Salesforce', 'AWS', 'SAML', 'Snowflake').\n
            - compliance_or_regulatory_signals: any mentions of compliance, audits, privacy, security standards, regulations.\n
            - scale_and_growth_signals: enterprise, multi-site, high volume, global, 'thousands', 'millions', fleet size, customers count—only if stated.\n
            - common_pain_points: problems the company claims to solve (cost, risk, manual work, downtime, visibility).\n
            - buyer_roles: Extract 5–15 plausible stakeholder job titles that an SDR could reach out to at this company.
                This is a GOAL-AGNOSTIC role inventory (do not try to choose "top roles" for any specific sales goal here).
                Rules for buyer_roles:
                - Prefer roles that plausibly influence purchase, evaluation, implementation, or operations for the company’s workflows.
                - Roles may be explicitly mentioned OR carefully inferred.
                - Inference is allowed ONLY if supported by evidence from core_workflows, technical_surface_area, compliance_or_regulatory_signals, scale_and_growth_signals, or common_pain_points.
                - Do NOT invent ultra-specific titles that are not supported by the text. Use common B2B titles.
                - Return ONLY job titles (no explanations), each as 2–6 words.
                - Remove duplicates and near-duplicates (e.g., keep only 'CFO' OR 'VP of Finance', not both).
                - If evidence is insufficient, return an empty list.\n\n
            
            - relevance_score: A number from 1-10 on how clearly this text defines the company's ICP (10 = very clear, 1 = vague marketing).\n
            - notable_keywords: short key phrases/terms repeated or emphasized in the markdown.\n
            - source_notes: brief notes on where signals came from (e.g., 'from homepage hero', 'from pricing page', 'from security section').\n\n
            Output requirements:\n
            - Return STRICT JSON matching the schema. No markdown, no extra keys.\n
            - Keep list items short (3–10 words each). Avoid long sentences in arrays.\n
            - Prefer concrete phrases copied/paraphrased from the markdown.\n
        """

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


RANK_COMPANIES_SYSTEM_PROMPT = """
            You are a cynical, gate-keeping Sales Ops manager.\n
            Your job is to rank companies as potential CUSTOMERS for the given sales goal.\n
            Return STRICT JSON only that matches the provided output schema. Do not include markdown or extra text.
        """

RANK_COMPANIES_USER_INSTRUCTION = """
            Rank all companies from best to worst fit for the sales_goal.\n
            CRITICAL:
            - If YOU THINK that a COMPANY may be a potential competitor, EXCLUDE them from the process completely.\n

            Scoring:\n
            - fit_score_0_to_100 must be an integer 0–100.\n
            - Use LeadCard evidence: core_workflows, technical_surface_area, compliance_or_regulatory_signals,\n
            scale_and_growth_signals, target_customers, common_pain_points.\n
            - Prioritize Technical Surface Area (integrations/APIs) and Core Workflows. A company with a clear workflow overlap is always a higher fit than one with just a category overlap.\n\n

            Outreach roles (goal-conditioned):\n
            - For each non-competitor company, choose exactly 3 top_outreach_roles that you would reach out to for this sales_goal.\n
            - top_outreach_roles MUST be chosen only from the company’s buyer_roles list (do not invent new titles).\n
            - Prefer economic buyer + internal champion + technical decision maker when applicable.\n
            - If the company has fewer than 3 buyer_roles, return as many as exist.\n\n

            Reasoning Architecture:
            - Reason MUST be 1-2 sentences. 
            - Format: 'Fit score of [X] assigned because [Cite specific workflow/product]. Target [Roles] as they manage [Cite specific tech surface/pain point].'\n\n

            Output:\n
            - Return JSON only with top-level key 'ranked'.
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
