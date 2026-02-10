import re
from urllib.parse import urlparse, urlsplit, urlunsplit
from collections import defaultdict
from publicsuffix2 import get_sld
from math import inf
from logger.universal_logger import setup_logger
# get the config
from utils.url_config import ALLOW, DENY_LOCALE_PREFIX, DENY_LOCALE_QUERY, DENY_PATH, DENY_SUBDOMAIN, POS_RULES, NEG_RULES, QUOTAS

logger = setup_logger('AI_SDR.Url_Utils')


def clean_title(title: str) -> str:
    """Clean up a title by removing dates, trailing periods or quotes, and truncating if needed."""
    if not title:
        return ""
    
    original_title = title
    
    title = title.strip().rstrip('.').strip('"\'')
    title = re.sub(r'^\d{4}[-\s]*\d{1,2}[-\s]*\d{1,2}[-\s]*', '', title)
    title = title.strip('- ').strip()
    
    # If title became empty after cleaning, return empty string
    if not title:
        logger.warning(f"Title became empty after cleaning: '{original_title}'")
        return ""
    
    # Log if we made changes to the title
    if title != original_title:
        logger.info(f"Cleaned title from '{original_title}' to '{title}'")
    
    return title

class CheckUrlDomain:
    def __init__(self, company_domain) -> None:
        self.BASE_DOMAIN = self.registrable_domain(company_domain)
        self.ranked_urls = []
        self.urls_by_type = defaultdict(list)
        self.seen_urls = set()

    def registrable_domain(self, url: str) -> str:
        host = (urlparse(url).hostname or "").lower()
        return get_sld(host) or ""

    def is_same_domain(self, url: str) -> bool:
        return self.registrable_domain(url) == self.BASE_DOMAIN

    def canonicalize(self, url: str) -> str:
        parts = urlsplit(url)
        scheme = parts.scheme.lower() or "https"
        netloc = parts.netloc.lower()
        path = parts.path.rstrip("/") or "/"
        return urlunsplit((scheme, netloc, path, "", ""))

    def _keep_url(self, url: str) -> bool:
        if url in self.seen_urls:
            return False
        
        self.seen_urls.add(url)
        u = self.canonicalize(url)
        if not self.is_same_domain(u):
            return False
        if DENY_SUBDOMAIN.search(u):
            return False
        if DENY_LOCALE_PREFIX.search(u) or DENY_LOCALE_QUERY.search(u):
            return False
        if DENY_PATH.search(u):
            return False
        return bool(ALLOW.search(u))
    
    def _filter_and_rank_url(self, url: str):
        u = self.canonicalize(url)
        p = urlsplit(u)
        path = p.path or "/"

        score = 0
        tags = []
        page_type = "other"

        # Negative first
        for rx, w in NEG_RULES:
            if rx.search(path):
                score += w
                tags.append(f"neg:{rx.pattern}")

        # Positive page types
        for name, rx, w in POS_RULES:
            if rx.search(path):
                score += w
                page_type = name
                tags.append(f"pos:{name}")
                break

        # Quality heuristics
        # Depth penalty
        depth = len([seg for seg in path.split("/") if seg])
        if depth > 2:
            score -= (depth - 2) * 3
            tags.append(f"depth:{depth}")

        # Numeric segment penalty (often IDs)
        if re.search(r"/\d{3,}(/|$)", path):
            score -= 8
            tags.append("neg:numeric_id")

        # File extension penalty
        if re.search(r"\.(pdf|png|jpg|jpeg|gif|zip)$", path, re.I):
            score -= 15
            tags.append("neg:file_ext")

        ranked = {
            "url": u,
            "score": score,
            "page_type": page_type,
            "tags": tags,
            "depth": depth,
        }
        self.urls_by_type[page_type].append(ranked)
        self.ranked_urls.append(ranked)
    
    def _select_top_k_urls(self, all_pages, k = 100):
        highest_score, lowest_score = -inf, inf
        for page in all_pages:
            if self._keep_url(page['url']):
                self._filter_and_rank_url(page['url'])
        logger.info(f"Filtered down to {len(self.ranked_urls)}. Removing {len(all_pages) - len(self.ranked_urls)} reduantant pages.")
        logger.info(f"Proceeding to shorted the top {k} pages according to page quotas.")
        selected = []
        used = set()

        # 1) Take up to cap from each type (in descending score order already)
        for t, cap in QUOTAS.items():
            for item in self.urls_by_type.get(t, [])[:cap]:
                u = item["url"]
                if u not in used:
                    selected.append(item)
                    used.add(u)
                    highest_score = max(highest_score, item["score"])
                    lowest_score = min(lowest_score, item["score"])

        # 2) Fill remaining slots with best overall leftovers
        if len(selected) < k:
            for item in self.ranked_urls:
                u = item["url"]
                if u in used:
                    continue
                selected.append(item)
                used.add(u)
                highest_score = max(highest_score, item["score"])
                lowest_score = min(lowest_score, item["score"])
                if len(selected) == k:
                    break
        
        logger.info(f"Completed the selection if {k} URLs for creation of Company Personas.")
        logger.info(f"(highest score, lowest score) : ({highest_score},{lowest_score})")
        return selected[:k]

