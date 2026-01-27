import re
from collections import defaultdict
from urllib.parse import urlparse
from utils.page_intents import INTENT_PATTERNS, NEGATIVE_PATTERNS, INTENT_WEIGHTS, INTENT_QUOTAS
from schema.PageIntent import PageIntent

JUNK_PATTERN = r".*\.(pdf|jpg|png|zip|docx|xml)$|.*(login|signup|privacy|terms|legal|contact).*"


class Discovery:

    def _classify_url(self, url: str) -> tuple[PageIntent, int]:
        path = (urlparse(url).path or "/").lower()

        for pat in NEGATIVE_PATTERNS:
            if re.search(pat, path):
                return PageIntent.IGNORE, -999

        best_intent = PageIntent.OTHER
        score = 0

        for intent, patterns in INTENT_PATTERNS.items():
            for pat in patterns:
                if re.search(pat, path):
                    score += INTENT_WEIGHTS[intent]
                    best_intent = intent

        depth = len([p for p in path.split("/") if p])
        score -= max(0, depth - 2) * 2

        if depth <= 2:
            score += 2

        return best_intent, score

    def _label_links(self, urls: list[str]):
        labeled = []

        for url in urls:
            intent, score = self._classify_url(url)
            labeled.append({
                "url": url,
                "intent": intent.value,
                "score": score
            })

        return sorted(labeled, key=lambda x: x["score"], reverse=True)

    def _select_sdr_pages(self, all_links: list[str], max_pages: int = 9):
        selected = []
        used = defaultdict(int)
        labeled_links = self._label_links(all_links)
        for item in labeled_links:
            intent = PageIntent(item["intent"])
            if intent == PageIntent.IGNORE:
                continue
            quota = INTENT_QUOTAS.get(intent, 0)
            if quota == 0:
                continue

            if used[intent] < quota:
                selected.append(item["url"])
                used[intent] += 1

            if len(selected) >= max_pages:
                break

        return selected
