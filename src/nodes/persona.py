import os
import json
from typing import Any, Dict, List, cast

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser

from logger.universal_logger import setup_logger
from schema.state import ResearchState, Persona
from utils.prompts import PERSONA_CREATION_PROMPT
from utils.json_utils import OUTPUT_STRUCT

logger = setup_logger(__name__)


class PersonaNode:
    """Creates the company Persona based on the information from research nodes"""

    def __init__(self) -> None:
        self.max_doc_length = 8000  # Maximum document content length
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        # Configure LangChain ChatGoogleGenerativeAI
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=gemini_key,
            max_retries=0
        )

    def _build_company_json(self, state: ResearchState) -> Dict:
        """Build a JSON string containing all research data for the LLM."""
        company = state.get('company', 'Unknown')

        curated_data = {
            "company": company,
            "company_url": state.get('company_url', ''),
            "industry": state.get('industry', 'Unknown'),
            "hq_location": state.get('hq_location', 'Unknown'),
            "site_scrape": {},
            "news_data": {},
            "trigger_data": {},
            "offering_data": {},
            "customer_data": {},
            "readiness_data": {},
        }

        # Add site_scrape data (limit content length)
        site_scrape = state.get('site_scrape', {})
        # Limit to top 10 pages
        for url, doc in list(site_scrape.items())[:10]:
            content = doc.get('raw_content', doc.get('content', ''))
            if len(content) > self.max_doc_length:
                content = content[:self.max_doc_length]
            curated_data["site_scrape"][url] = {
                "raw_content": content,
                "source": doc.get('source', 'unknown')
            }

        # Add curated research data (limit content length)
        data_types = [
            ('news_data', 'news'),
            ('trigger_data', 'triggers'),
            ('offering_data', 'offerings'),
            ('customer_data', 'customers'),
            ('readiness_data', 'readiness'),
        ]

        for state_key, _ in data_types:
            data = state.get(state_key, {})
            # Limit to top 15 per category
            for url, doc in list(data.items())[:15]:
                content = doc.get('content', doc.get('raw_content', ''))
                if len(content) > self.max_doc_length:
                    content = content[:self.max_doc_length]
                curated_data[state_key][url] = {
                    "title": doc.get('title', ''),
                    "content": content,
                    "url": url,
                    "score": doc.get('score', 0.0)
                }

        return curated_data

    def _parse_persona_response(self, response: str) -> Persona:
        """Parse LLM JSON response into Persona TypedDict."""
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()

        try:
            data = json.loads(response)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Response was: {response[:500]}")
            # Return minimal persona on error - need to get company from state context
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")

        # ---- core_products ----
        core_products: List[Dict[str, str]] = []
        for product in data.get("core_products", []) or []:
            if isinstance(product, dict):
                core_products.append({
                    "name": str(product.get("name", "")),
                    "description": str(product.get("description", "")),
                })
            elif isinstance(product, str):
                core_products.append({"name": product, "description": ""})

        # ---- target_market (NOTE: singular in your JSON) ----
        target_market = data.get("target_market", {})
        if isinstance(target_market, str):
            target_market = {"industries": [],
                             "ideal_customer_profile": target_market}
        elif not isinstance(target_market, dict):
            target_market = {}

        # ---- sales_triggers ----
        sales_triggers = data.get("sales_triggers", {})
        if isinstance(sales_triggers, str):
            sales_triggers = {"recent_news": sales_triggers,
                              "strategic_priorities": ""}
        elif not isinstance(sales_triggers, dict):
            sales_triggers = {}

        # Map your JSON keys to the keys your Persona expects
        recent_news = sales_triggers.get(
            "recent_news") or sales_triggers.get("recent_funding_or_news", "")
        strategic_priorities = sales_triggers.get(
            "strategic_priorities") or sales_triggers.get("strategic_priorities_2025_2026", "")

        # ---- sales_intelligence ----
        sales_intelligence = data.get("sales_intelligence", {})
        if isinstance(sales_intelligence, str):
            sales_intelligence = {"green_flags": [],
                                  "red_flags": [], "compliance_standards": []}
        elif not isinstance(sales_intelligence, dict):
            sales_intelligence = {}

        # ---- impact_metrics (safe) ----
        impact_metrics: List[Dict[str, Any]] = []
        for metric in data.get("impact_metrics", []) or []:
            if isinstance(metric, dict):
                impact_metrics.append({
                    "case_study": metric.get("case_study", ""),
                    "result": metric.get("result", ""),
                })

        persona: Persona = cast(Persona, {
            "company_name": data.get("company_name", data.get("company", "Unknown")),
            "industry": data.get("industry", "Unknown"),
            "hq_location": data.get("hq_location", "Unknown"),
            "mission_statement": data.get("mission_statement", data.get("executive_summary", "")),
            "core_products": core_products,
            "target_markets": cast(Dict[str, Any], {
                "industries": target_market.get("industries", []),
                "ideal_customer_profile": target_market.get("ideal_customer_profile", ""),
            }),
            "sales_triggers": cast(Dict[str, Any], {
                "recent_news": recent_news,
                "strategic_priorities": strategic_priorities,
            }),
            "impact_metrics": cast(List[Dict[str, Any]], impact_metrics),
            "sales_intelligence": cast(Dict[str, Any], {
                "green_flags": sales_intelligence.get("green_flags", []),
                "red_flags": sales_intelligence.get("red_flags", []),
                "compliance_standards": sales_intelligence.get("compliance_standards", []),
            }),
        })

        return persona

    async def create_personas(self, state: ResearchState) -> ResearchState:
        """Create company persona from curated research data."""
        company = state.get('company', 'Unknown')
        logger.info(f"Creating persona for {company}")

        company_json = self._build_company_json(state)
        logger.info(
            f"Built company JSON context ({len(company_json)} chars)")

        formatted_prompt = PERSONA_CREATION_PROMPT.format(
            company_json=company_json, output_structure=OUTPUT_STRUCT, year=2025-2026)

        chain = self.llm | StrOutputParser()

        try:
            # Invoke LLM with formatted prompt
            response = await chain.ainvoke(formatted_prompt)
            logger.info(f"Received LLM response ({len(response)} chars)")
            persona = self._parse_persona_response(response)

            # Add persona to state
            state['persona'] = persona

            logger.info(f"Successfully created persona for {company}")
            logger.debug(
                f"Persona: {json.dumps(persona, indent=2, default=str)}")

        except Exception as e:
            logger.error(
                f"Error creating persona for {company}: {e}", exc_info=True)
            # Add empty persona on error
            state['persona'] = cast(Persona, {
                "company_name": company,
                "industry": state.get('industry', 'Unknown'),
                "hq_location": state.get('hq_location', 'Unknown'),
                "mission_statement": "",
                "core_products": [],
                "target_markets": {"industries": [], "ideal_customer_profile": ""},
                "sales_triggers": {"recent_news": "", "strategic_priorities": ""},
                "impact_metrics": [{"efficiency": "", "accuracy": ""}],
                "sales_intelligence": {"green_flags": [], "red_flags": [], "compliance_standards": []}
            })

        return state

    async def run(self, state: ResearchState) -> ResearchState:
        return await self.create_personas(state)
