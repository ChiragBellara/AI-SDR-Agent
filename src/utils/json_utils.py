import json
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, HttpUrl, ValidationError


class SourceEntry(BaseModel):
    name: str
    url: HttpUrl


def validate_sources(data):
    """Checks if the uploaded list matches our expected schema."""
    if not isinstance(data, list):
        return False, "Data must be a JSON list of objects."

    try:
        # Validate each item in the list
        validated_data = [SourceEntry(**item) for item in data]
        return True, validated_data
    except ValidationError as e:
        # Extract the specific error for the UI
        error_msg = f"Invalid format in entry: {e.errors()[0]['loc']} - {e.errors()[0]['msg']}"
        return False, error_msg
    except Exception as e:
        return False, str(e)


def _parse_first_json(raw: str) -> Optional[dict]:
    raw = raw.strip()

    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1].strip()
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0].strip()

    if raw.startswith("["):
        arr = json.loads(raw)
        if not arr:
            return None
        return arr[0] if isinstance(arr[0], dict) else None

    decoder = json.JSONDecoder()
    try:
        obj, _ = decoder.raw_decode(raw)
        return obj if isinstance(obj, dict) else None
    except Exception:
        return None


def _merge_lead_cards(cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    merged: Dict[str, Any] = {}

    scalar_fields = ["company_name", "category", "one_liner"]
    for f in scalar_fields:
        for c in cards:
            v = c.get(f)
            if v:
                merged[f] = v
                break
        merged.setdefault(f, None)

    list_fields = [
        "products_or_platform",
        "target_customers",
        "core_workflows",
        "technical_surface_area",
        "integrations_or_stack_hints",
        "compliance_or_regulatory_signals",
        "scale_and_growth_signals",
        "common_pain_points",
        "buyer_roles",
        "notable_keywords",
        "source_notes",
    ]

    for f in list_fields:
        seen = set()
        out = []
        for c in cards:
            vals = c.get(f) or []
            if isinstance(vals, list):
                for item in vals:
                    s = str(item).strip()
                    if s and s.lower() not in seen:
                        seen.add(s.lower())
                        out.append(s)
        merged[f] = out

    return merged

from typing import Any, Dict, List, Optional, Tuple
from copy import deepcopy


def _merge_company_personas(cards: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge a list of *partial* Company Persona dicts (new schema) into a single persona dict.

    Strategy:
      - Scalars: first non-empty wins (per path)
      - Lists of strings: union (case-insensitive) preserving first-seen order
      - Lists of objects: de-dupe by a stable key (e.g., url, name+title, etc.)
      - Dicts: recurse
    """

    def _is_nonempty(v: Any) -> bool:
        if v is None:
            return False
        if isinstance(v, str):
            return v.strip() != ""
        if isinstance(v, (list, dict, set, tuple)):
            return len(v) > 0
        return True

    def _get(d: Dict[str, Any], path: str, default=None):
        cur = d
        for k in path.split("."):
            if not isinstance(cur, dict) or k not in cur:
                return default
            cur = cur[k]
        return cur

    def _ensure_path(out: Dict[str, Any], path: str) -> Dict[str, Any]:
        cur = out
        parts = path.split(".")
        for k in parts[:-1]:
            if k not in cur or not isinstance(cur[k], dict):
                cur[k] = {}
            cur = cur[k]
        return cur

    def _set(out: Dict[str, Any], path: str, value: Any) -> None:
        parent = _ensure_path(out, path)
        parent[path.split(".")[-1]] = value

    def _merge_string_lists(*lists: Optional[List[Any]]) -> List[str]:
        seen = set()
        out: List[str] = []
        for lst in lists:
            if not lst or not isinstance(lst, list):
                continue
            for item in lst:
                s = str(item).strip()
                if not s:
                    continue
                key = s.lower()
                if key in seen:
                    continue
                seen.add(key)
                out.append(s)
        return out

    def _obj_key(obj: Any, keys: List[str]) -> Optional[Tuple[str, ...]]:
        """Build a de-dupe key from a dict object using a list of dotted paths."""
        if not isinstance(obj, dict):
            return None
        vals: List[str] = []
        for k in keys:
            v = _get(obj, k, None)
            if v is None:
                return None
            s = str(v).strip()
            if not s:
                return None
            vals.append(s.lower())
        return tuple(vals)

    def _merge_object_lists(
        lists: List[List[Any]],
        key_paths: List[str],
        keep: str = "first",
    ) -> List[Dict[str, Any]]:
        """
        Merge lists of dict objects, de-duping by key_paths.
        keep="first" keeps first seen object for a given key; "last" overwrites with later.
        """
        out: List[Dict[str, Any]] = []
        idx: Dict[Tuple[str, ...], int] = {}

        for lst in lists:
            if not lst or not isinstance(lst, list):
                continue
            for item in lst:
                if not isinstance(item, dict):
                    continue
                k = _obj_key(item, key_paths)
                if k is None:
                    # No stable key => append as-is (but avoid identical dict duplicates)
                    if item not in out:
                        out.append(item)
                    continue

                if k not in idx:
                    idx[k] = len(out)
                    out.append(item)
                else:
                    if keep == "last":
                        out[idx[k]] = item
                    else:
                        # keep first; but we can deep-merge fields to enrich
                        out[idx[k]] = _deep_merge_dicts(out[idx[k]], item)
        return out

    def _deep_merge_dicts(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dicts:
          - Scalars: first non-empty wins (a has priority, b fills gaps)
          - Lists of strings: union
          - Lists of dicts: concatenate (callers should do smarter merges where needed)
          - Dicts: recurse
        """
        out = deepcopy(a)

        for k, bv in (b or {}).items():
            av = out.get(k)

            if isinstance(av, dict) and isinstance(bv, dict):
                out[k] = _deep_merge_dicts(av, bv)
                continue

            if isinstance(av, list) and isinstance(bv, list):
                # If list is list[str], union; otherwise concat with de-dupe by exact dict
                if all(isinstance(x, (str, int, float, bool)) or x is None for x in av + bv):
                    out[k] = _merge_string_lists(av, bv)
                else:
                    merged = deepcopy(av)
                    for x in bv:
                        if x not in merged:
                            merged.append(x)
                    out[k] = merged
                continue

            # Scalars / mismatched: first non-empty wins
            if _is_nonempty(av):
                continue
            if _is_nonempty(bv):
                out[k] = bv

        return out

    merged: Dict[str, Any] = {}

    # --------------------------
    # 1) Scalars: first non-empty wins
    # --------------------------
    scalar_paths = [
        # company identity
        "company.name",
        "company.legal_name",
        "company.website",
        "company.domains.primary",
        "company.hq.city",
        "company.hq.region",
        "company.hq.country",
        # description
        "company.description.one_liner",
        "company.description.positioning",
        "company.description.category",
        # stage/size
        "company.stage_and_size.employee_range",
        "company.stage_and_size.revenue_range",
        "company.stage_and_size.funding_stage",
        "company.stage_and_size.public_company",
        "company.stage_and_size.ticker",
        # ICP
        "icp_fit.fit_score",
        "icp_fit.fit_tier",
        # budget/pricing
        "budget_and_buying.pricing.has_pricing_page",
        "budget_and_buying.pricing.pricing_url",
        "budget_and_buying.pricing.pricing_model",
        "budget_and_buying.pricing.starts_at_usd",
        "budget_and_buying.pricing.enterprise_plan_present",
        "budget_and_buying.pricing.quote_required",
        "budget_and_buying.procurement_signals.sso_saml_supported",
        "budget_and_buying.procurement_signals.legal_readiness",
        "budget_and_buying.sales_motion.cta_primary",
        "budget_and_buying.sales_motion.demo_required",
        "budget_and_buying.sales_motion.trial_available",
        # tech
        "tech_environment.integrations_and_ecosystem.api_maturity",
        # sources
        "sources.last_updated_utc",
        "sources.notes",
    ]

    for path in scalar_paths:
        chosen = None
        for c in cards:
            v = _get(c, path, None)
            if _is_nonempty(v):
                chosen = v
                break
        if chosen is not None:
            _set(merged, path, chosen)

    # Ensure these keys exist even if empty (optional; keeps downstream stable)
    # (Only doing for top-level containers we know we want.)
    merged.setdefault("company", {})
    merged.setdefault("icp_fit", {})
    merged.setdefault("products_and_offering", {})
    merged.setdefault("customer_profile", {})
    merged.setdefault("pain_points_and_use_cases", {})
    merged.setdefault("budget_and_buying", {})
    merged.setdefault("tech_environment", {})
    merged.setdefault("organization_and_people", {})
    merged.setdefault("messaging_and_outreach", {})
    merged.setdefault("web_signals", {})
    merged.setdefault("risk_and_disqualifiers", {})
    merged.setdefault("next_steps", {})
    merged.setdefault("sources", {})

    # --------------------------
    # 2) Lists of strings: union
    # --------------------------
    list_paths = [
        "company.domains.subdomains_seen",
        "company.geo_coverage",
        "company.description.keywords",
        "icp_fit.fit_rationale.strong_signals",
        "icp_fit.fit_rationale.weak_signals",
        "icp_fit.fit_rationale.red_flags",
        "icp_fit.target_segments.customer_size",
        "icp_fit.target_segments.industries_served",
        "icp_fit.target_segments.regions_served",
        "customer_profile.industries",
        "pain_points_and_use_cases.stated_problems",
        "pain_points_and_use_cases.use_cases",
        "pain_points_and_use_cases.value_metrics.cost",
        "pain_points_and_use_cases.value_metrics.time",
        "pain_points_and_use_cases.value_metrics.risk",
        "pain_points_and_use_cases.value_metrics.revenue",
        "pain_points_and_use_cases.urgency_signals.regulatory_pressure",
        "pain_points_and_use_cases.urgency_signals.safety_pressure",
        "pain_points_and_use_cases.urgency_signals.downtime_pressure",
        "pain_points_and_use_cases.urgency_signals.scale_pressure",
        "budget_and_buying.procurement_signals.security_certifications",
        "budget_and_buying.procurement_signals.compliance_standards",
        "budget_and_buying.procurement_signals.data_residency_options",
        "tech_environment.inferred_stack.frontend",
        "tech_environment.inferred_stack.backend",
        "tech_environment.inferred_stack.cloud",
        "tech_environment.inferred_stack.data",
        "tech_environment.inferred_stack.observability",
        "tech_environment.integrations_and_ecosystem.tools_they_integrate_with",
        "tech_environment.integrations_and_ecosystem.partner_ecosystem",
        "tech_environment.signals.uses_crm",
        "tech_environment.signals.uses_support_platform",
        "tech_environment.signals.uses_marketing_tools",
        "risk_and_disqualifiers.deal_risks",
        "risk_and_disqualifiers.competitive_landscape.competitors_mentioned",
        "risk_and_disqualifiers.competitive_landscape.alternatives_likely",
        "sources.scraped_urls",
    ]

    for path in list_paths:
        lists = []
        for c in cards:
            v = _get(c, path, None)
            if isinstance(v, list):
                lists.append(v)
        if lists:
            _set(merged, path, _merge_string_lists(*lists))
        else:
            # keep absent if no input; downstream can default
            pass

    # --------------------------
    # 3) Lists of objects: merge with stable keys
    # --------------------------

    # products_and_offering.primary_products: key by name (fallback enrich/merge)
    prod_lists = [(_get(c, "products_and_offering.primary_products", []) or []) for c in cards]
    merged_products = _merge_object_lists(prod_lists, key_paths=["name"], keep="first")
    if merged_products:
        _set(merged, "products_and_offering.primary_products", merged_products)

    # customer_profile.customer_examples: key by proof_url if present, else name
    cust_lists = [(_get(c, "customer_profile.customer_examples", []) or []) for c in cards]
    # do two-pass: prefer proof_url key, then name
    merged_cust = _merge_object_lists(cust_lists, key_paths=["proof_url"], keep="first")
    merged_cust = _merge_object_lists([merged_cust], key_paths=["name"], keep="first")
    if merged_cust:
        _set(merged, "customer_profile.customer_examples", merged_cust)

    # organization_and_people.leadership: key by (name,title)
    lead_lists = [(_get(c, "organization_and_people.leadership", []) or []) for c in cards]
    merged_leadership = _merge_object_lists(lead_lists, key_paths=["name", "title"], keep="first")
    if merged_leadership:
        _set(merged, "organization_and_people.leadership", merged_leadership)

    # organization_and_people.hiring_signals.open_roles: key by url if present else title+location
    roles_lists = [(_get(c, "organization_and_people.hiring_signals.open_roles", []) or []) for c in cards]
    merged_roles = _merge_object_lists(roles_lists, key_paths=["url"], keep="first")
    merged_roles = _merge_object_lists([merged_roles], key_paths=["title", "location"], keep="first")
    if merged_roles:
        _set(merged, "organization_and_people.hiring_signals.open_roles", merged_roles)

    # messaging_and_outreach.personalization_hooks: key by (hook,source_url)
    hook_lists = [(_get(c, "messaging_and_outreach.personalization_hooks", []) or []) for c in cards]
    merged_hooks = _merge_object_lists(hook_lists, key_paths=["hook", "source_url"], keep="first")
    if merged_hooks:
        _set(merged, "messaging_and_outreach.personalization_hooks", merged_hooks)

    # messaging_and_outreach.value_hypotheses: key by hypothesis
    hyp_lists = [(_get(c, "messaging_and_outreach.value_hypotheses", []) or []) for c in cards]
    merged_hyps = _merge_object_lists(hyp_lists, key_paths=["hypothesis"], keep="first")
    if merged_hyps:
        _set(merged, "messaging_and_outreach.value_hypotheses", merged_hyps)

    # web_signals.high_signal_pages: key by url
    hsp_lists = [(_get(c, "web_signals.high_signal_pages", []) or []) for c in cards]
    merged_hsp = _merge_object_lists(hsp_lists, key_paths=["url"], keep="first")
    if merged_hsp:
        _set(merged, "web_signals.high_signal_pages", merged_hsp)

    # risk_and_disqualifiers.disqualifiers: key by reason
    disq_lists = [(_get(c, "risk_and_disqualifiers.disqualifiers", []) or []) for c in cards]
    merged_disq = _merge_object_lists(disq_lists, key_paths=["reason"], keep="first")
    if merged_disq:
        _set(merged, "risk_and_disqualifiers.disqualifiers", merged_disq)

    # --------------------------
    # 4) Merge a few nested dicts where "first non-empty wins" isn't enough
    # --------------------------

    # platform_signals (dict)
    ps = {}
    for c in cards:
        v = _get(c, "products_and_offering.platform_signals", None)
        if isinstance(v, dict):
            ps = _deep_merge_dicts(ps, v)
    if ps:
        _set(merged, "products_and_offering.platform_signals", ps)

    # customer_profile.logo_tier_summary (dict)
    lts = {}
    for c in cards:
        v = _get(c, "customer_profile.logo_tier_summary", None)
        if isinstance(v, dict):
            lts = _deep_merge_dicts(lts, v)
    if lts:
        _set(merged, "customer_profile.logo_tier_summary", lts)

    # messaging_and_outreach.positioning_language (dict)
    pl = {}
    for c in cards:
        v = _get(c, "messaging_and_outreach.positioning_language", None)
        if isinstance(v, dict):
            pl = _deep_merge_dicts(pl, v)
    if pl:
        _set(merged, "messaging_and_outreach.positioning_language", pl)

    # web_signals.ignore_rules_applied (dict)
    ira = {}
    for c in cards:
        v = _get(c, "web_signals.ignore_rules_applied", None)
        if isinstance(v, dict):
            ira = _deep_merge_dicts(ira, v)
    if ira:
        _set(merged, "web_signals.ignore_rules_applied", ira)

    return merged
