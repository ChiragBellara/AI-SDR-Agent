import re

ALLOW = re.compile(
    r"/("
    r"products?|platform|features?|capabilities"
    r"|solutions?|use-cases?|usecases"
    r"|industries?|verticals?"
    r"|customers|customer-stories|testimonials|case-studies|success-stories"
    r"|pricing|plans"
    r"|integrations?|partners?|marketplace"
    r"|api|developers?|docs|documentation"
    r"|security|trust|trust-center|compliance|soc-2|privacy/security"
    r"|careers?|jobs"
    r"|about|company|leadership|team"
    r"|contact|request-demo|demo"
    r")(/|$)",
    re.I
)

DENY_PATH = re.compile(
    r"/("
    r"login|signup|register|sign-in|sign_in"
    r"|privacy$|terms$|cookie|cookies"
    r"|press|newsroom|media"
    r"|events?|webinars?"
    r"|blog"
    r"|shop|store|cart|checkout"
    r"|marketplace"
    r")(/|$)",
    re.I
)

DENY_SUBDOMAIN = re.compile(r"^https?://(shop|store)\.", re.I)

# Locale as FIRST path segment only
DENY_LOCALE_PREFIX = re.compile(
    r"^https?://[^/]+/"
    r"("
    r"[a-z]{2}(-[a-z]{2})?"          # fr, fr-ca, en-gb
    r"|zh-(cn|tw)"                   # zh-cn, zh-tw
    r")"
    r"(/|$)",
    re.I
)

# Also deny explicit locale query params
DENY_LOCALE_QUERY = re.compile(r"[?&](lang|locale|country)=", re.I)

POS_RULES = [
    ("pricing",        re.compile(r"/(pricing|plans|plan|package|packages)(/|$)", re.I),  30),
    ("customers",      re.compile(r"/(customers|customer-stories|testimonials)(/|$)", re.I), 28),
    ("case_studies",   re.compile(r"/(case-studies|success-stories|stories)(/|$)", re.I), 28),
    ("security",       re.compile(r"/(security|trust|trust-center|compliance|soc-2|soc2|iso)(/|$)", re.I), 26),
    ("integrations",   re.compile(r"/(integrations|integration|partners|partner)(/|$)", re.I), 24),
    ("api_devs",       re.compile(r"/(api|developers|developer|docs|documentation|sdk|webhooks)(/|$)", re.I), 24),
    ("products",       re.compile(r"/(products?|product|platform|features?|capabilities)(/|$)", re.I), 22),
    ("solutions",      re.compile(r"/(solutions?|use-cases?|usecases)(/|$)", re.I), 20),
    ("industries",     re.compile(r"/(industries?|verticals?|sectors)(/|$)", re.I), 18),
    ("about",          re.compile(r"/(about|company|leadership|team|who-we-are)(/|$)", re.I), 16),
    ("careers",        re.compile(r"/(careers?|jobs|open-roles|openings)(/|$)", re.I), 14),
    ("contact",        re.compile(r"/(contact|request-demo|demo|talk-to-sales|get-a-demo)(/|$)", re.I), 12),
]

# Negative signals (hard penalties)
NEG_RULES = [
    (re.compile(r"/(blog|press|newsroom|news|media)(/|$)", re.I), -35),
    (re.compile(r"/(events?|webinars?|conference|meetup)(/|$)", re.I), -30),
    (re.compile(r"/(login|signup|register|sign-in|signin)(/|$)", re.I), -50),
    (re.compile(r"/(privacy|terms|legal|cookies?)(/|$)", re.I), -40),
    (re.compile(r"/(shop|store|cart|checkout)(/|$)", re.I), -60),
    (re.compile(r"/resources/marketplace(/|$)", re.I), -40),
]


QUOTAS = {
    "pricing": 5,
    "security": 5,
    "integrations": 10,
    "api_devs": 10,
    "products": 15,
    "solutions": 15,
    "industries": 10,
    "customers": 20,
    "case_studies": 5,
    "about": 5,
    "careers": 3,
    "contact": 2,
}