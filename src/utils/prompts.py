CRAWL_INSTRUCTION = """
            You are an AI-SDR agent building a reusable company 'LeadCard' memory object.\n
            From the provided markdowns, populate the LeadCard schema with ONLY what is explicitly supported by the text.\n
            Do NOT guess or infer details that are not present. If a field is not supported, use an empty list or null.\n\n
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
            - buyer_roles: roles mentioned or clearly implied by text (e.g., 'IT admin', 'Ops manager', 'CISO'). Only include if supported.\n
            - relevance_score: A number from 1-10 on how clearly this text defines the company's ICP (10 = very clear, 1 = vague marketing).\n
            - notable_keywords: short key phrases/terms repeated or emphasized in the markdown.\n
            - source_notes: brief notes on where signals came from (e.g., 'from homepage hero', 'from pricing page', 'from security section').\n\n
            Output requirements:\n
            - Return STRICT JSON matching the schema. No markdown, no extra keys.\n
            - Keep list items short (3–10 words each). Avoid long sentences in arrays.\n
            - Prefer concrete phrases copied/paraphrased from the markdown.\n"""
