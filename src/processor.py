from litellm import max_tokens
from pydantic import BaseModel, Field, ValidationError
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from typing import List, Tuple, Optional
from pathlib import Path
import json
import os
from dotenv import load_dotenv
from company_identity import CompanyIdentity


class IdentityProcessor:
    def __init__(self, provider="gpt-4o-mini", file_to_read=None):
        load_dotenv()
        self.model = provider
        if not file_to_read:
            raise Exception("File Not Found")
        self.content = file_to_read.read_text()
        print(
            f"Loaded the model and the file successfully. File Size: {len(self.content)}")

    def _build_prompt(self):
        schema_example = {
            "company_name": "Atlassian",
            "value_prop": "Providing collaboration and productivity tools for software teams...",
            "target_icp": {
                "industry": "Software Development, Enterprise IT",
                "titles": ["CTO", "Engineering Manager", "Product Owner"],
                "pain_points": ["Siloed communication", "Delayed shipping cycles"]
            }
        }
        # system_prompt = f"""
        #     You are an information extraction engine.
        #     Task:
        #     Read the markdown content and extract a CompanyIdentity object.

        #     Rules:
        #     - Output MUST be valid JSON (no markdown fences, no commentary).
        #     - If a field is not explicitly stated, infer conservatively from context.
        #     - target_icp and tech_stack_hints must be arrays of strings (can be empty, but prefer best-effort).
        #     - value_proposition should be concise (1–2 sentences max).

        #     Return JSON matching this shape exactly:
        #     {json.dumps(schema_example, indent=2)}
        # """
        system_prompt = (
            "You extract structured information from markdown. Return only the fields required by the schema.")
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Extract from this markdown:\n\n{markdown}")
        ])
        return prompt

    def _get_llm(self):
        provider = os.getenv("LLM_PROVIDER", "openai").lower()
        temperature = float(os.getenv("LLM_TEMPERATURE", "0"))

        if provider == "openai":
            return ChatOpenAI(
                model=self.model,
                temperature=temperature
            )

        if provider == "anthropic":
            return ChatAnthropic(
                model_name=self.model,
                timeout=10,
                stop=None,
                temperature=temperature,
            )

        raise Exception("Model Not Found")

    def _call_llm(self):
        system_prompt = self._build_prompt()
        print("System Prompt Generation Successful")
        llm_to_use = self._get_llm()
        print(f"Using {llm_to_use.get_name()}")
        structured_llm = llm_to_use.with_structured_output(
            CompanyIdentity, strict=True)
        chain = system_prompt | structured_llm
        return chain.invoke({"markdown": self.content})
