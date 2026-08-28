import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote, urlparse, parse_qs
import time


# =========================================================
# GOOGLE APPS SCRIPT
# =========================================================

APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbzZvszdkfDv-ELPj_Hu1VGSdIGhBEATnQP0m2KHx6cDxjXMCXFOoaH0yOh5GzHVj8hk"
    "/exec"
)


# =========================================================
# SEARCH ENGINE
# =========================================================

GOOGLE_URL = "https://www.google.com/search?q={}"


# =========================================================
# PLATFORMS
# =========================================================

PLATFORMS = {
    "Facebook": "facebook.com",
    "LinkedIn": "linkedin.com"
}


# =========================================================
# KEYWORDS
# =========================================================

KEYWORDS = {

    "GENERAL": [
        "looking for a job",
        "looking for work",
        "seeking employment",
        "looking for job opportunities",
        "looking for new opportunities",
        "open to work",
        "open for opportunities",
        "looking for hybrid",
        "looking for remote"
    ],

    "HEALTHCARE": [
        "fresh graduate pharmacist",
        "fresh graduate pharmacist looking for a job",
        "licensed pharmacist seeking employment",
        "licensed pharmacist",
        "i am registered nurse",
        "phrn/usrn",
        "phrn looking for work",
        "phrn seeking employment",
        "phrn looking for opportunities",
        "usrn looking for a job",
        "usrn looking for work",
        "usrn seeking employment",
        "usrn looking for opportunities"
    ],

    "BPO_AGENT": [
        "bpo applicant looking for a job",
        "bpo agent looking for work",
        "call center agent looking for a job",
        "i have bpo background"
    ]
}


# =========================================================
# HTTP SESSION
# =========================================================

session = requests.Session()

session.headers.update({

    "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0.0.0 Safari/537.36",

    "Accept":
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8",

    "Accept-Language":
        "en-US,en;q=0.9"

})


# =========================================================
# CLEAN TEXT
# =========================================================

def clean(value):

    if not value:
        return ""

    return " ".join(
        str(value).split()
    ).strip()


# =========================================================
# GOOGLE URL CLEANER
# =========================================================

def unwrap_url(href):

    if not href:
        return ""

    if href.startswith("/url?"):

        parsed = urlparse(href)

        params = parse_qs(
            parsed.query
        )

        if "q" in params:
            return params["q"][0]

        if "url" in params:
            return params["url"][0]

    if href.startswith("http://"):
        return href

    if href.startswith("https://"):
        return href

    return ""


# =========================================================
# CHECK PLATFORM
# =========================================================

def belongs_to_platform(url, domain):

    try:

        host = (
            urlparse(url)
            .netloc
            .lower()
        )

        return domain in host

    except Exception:

        return False


# =========================================================
# BUILD QUERY
# =========================================================

def build_query(domain, keywords):

    keyword_query = " OR ".join(
        f'"{keyword}"'
        for keyword in keywords
    )

    return (
        f"site:{domain} "
        f"({keyword_query})"
    )


# =========================================================
# DETECT MATCHING KEYWORD
# =========================================================

def detect_keyword(text, keywords):

    text = text.lower()

    matches = []

    for keyword in keywords:

        if keyword.lower() in text:

            matches.append(
                keyword
            )

    if not matches:
        return ""

    # longest matching keyword first
    matches.sort(
        key=len,
        reverse=True
    )

    return matches[0]


# =========================================================
# DETECT CATEGORY
# =========================================================

def detect_category(text):

    lower = text.lower()

    for category, keywords in KEYWORDS.items():

        for keyword in keywords:

            if keyword.lower() in lower:

                return category, keyword

    return "", ""


# =========================================================
# PROFESSION
# =========================================================

def detect_profession(text):

    lower = text.lower()

    if "pharmacist" in lower:
        return "Pharmacist"

    if "phrn" in lower:
        return "PHRN"

    if "usrn" in lower:
        return "USRN"

    if "registered nurse" in lower:
        return "Registered Nurse"

    if "call center" in lower:
        return "Call Center Agent"

    if "bpo" in lower:
        return "BPO Agent"

    return ""


# =========================================================
# SCORE
# =========================================================

def calculate_score(text):

    lower = text.lower()

    score = 0

    for category in KEYWORDS:

        for keyword in KEYWORDS[category]:

            if keyword.lower() in lower:

                if (
                    "looking for a job"
                    in keyword.lower()

                    or

                    "looking for work"
                    in keyword.lower()

                    or

                    "seeking employment"
                    in keyword.lower()
                ):

                    score += 30

                else:

                    score += 15

    return min(score, 100)


# =========================================================
# GOOGLE SEARCH
# =========================================================

def google_search(
    platform,
    domain,
    category
):

    keywords = KEYWORDS[category]

    query = build_query(
        domain,
        keywords
    )

    url = GOOGLE_URL.format(
        quote(query)
    )

    print()
    print("=" * 70)
    print("SEARCH")
    print("=" * 70)

    print(
        f"Platform : {platform}"
    )

    print(
        f"Category : {category}"
    )

    print(
        f"Query    : {query}"
    )

    try:

        response = session.get(
            url,
            timeout=30
        )

        print(
            f"HTTP Status: "
            f"{response.status_code}"
        )

        # -------------------------------------------------
        # RATE LIMIT
        # -------------------------------------------------

        if response.status_code == 429:

            print(
                "GOOGLE RATE LIMIT DETECTED."
            )

            print(
                "Waiting before stopping..."
            )

            time.sleep(15)

            return []

        if response.status_code != 200:

            print(
                "Google request failed."
            )

            return []


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        results = []


        # -------------------------------------------------
        # FIND GOOGLE RESULT TITLES
        # -------------------------------------------------

        for h3 in soup.find_all("h3"):

            title = clean(
                h3.get_text(
                    " ",
                    strip=True
                )
            )

            if not title:
                continue


            link = h3.find_parent("a")

            if not link:
                continue


            href = link.get(
                "href",
                ""
            )

            result_url = unwrap_url(
                href
            )


            if not result_url:
                continue


            if not belongs_to_platform(
                result_url,
                domain
            ):

                continue


            # Get nearby result text

            parent = h3.parent

            if parent:

                container = (
                    parent.parent
                    or parent
                )

            else:

                container = h3


            snippet = clean(
                container.get_text(
                    " ",
                    strip=True
                )
            )


            combined = (
                title +
                " " +
                snippet
            )


            matched_keyword = (
                detect_keyword(
                    combined,
                    keywords
                )
            )


            if not matched_keyword:

                continue


            results.append({

                "platform":
                    platform,

                "category":
                    category,

                "keyword":
                    matched_keyword,

                "title":
                    title,

                "snippet":
                    snippet,

                "url":
                    result_url

            })


        # -------------------------------------------------
        # REMOVE DUPLICATES
        # -------------------------------------------------

        unique = []

        seen = set()

        for result in results:

            url = result["url"]

            if url in seen:
                continue

            seen.add(url)

            unique.append(
                result
            )


        print(
            f"Matching public results: "
            f"{len(unique)}"
        )


        return unique


    except requests.RequestException as error:

        print(
            f"REQUEST ERROR: {error}"
        )

        return []


# =========================================================
# CREATE CANDIDATE
# =========================================================

def create_candidate(result):

    text = (
        result["title"]
        + " "
        + result["snippet"]
    )

    return {

        "platform":
            result["platform"],

        "name":
            result["title"],

        "email":
            "",

        "phone":
            "",

        "profession":
            detect_profession(text),

        "resume_url":
            "",

        "url":
            result["url"],

        "text":
            text,

        "score":
            calculate_score(text),

        "keyword":
            result["keyword"],

        "category":
            result["category"],

        "found_at":
            datetime.now().isoformat()

    }


# =========================================================
# SEND TO GOOGLE SHEET
# =========================================================

def send_to_google(candidate):

    print()
    print("Sending candidate to Google Apps Script...")

    try:

        response = session.post(

            APPS_SCRIPT_URL,

            json=candidate,

            timeout=30,

            allow_redirects=True

        )

        print(
            f"Google HTTP Status: "
            f"{response.status_code}"
        )

        print(
            "Google Response:"
        )

        print(
            response.text
        )

        return response


    except requests.RequestException as error:

        print(
            f"GOOGLE ERROR: {error}"
        )

        return None


# =========================================================
# PROCESS RESULT
# =========================================================

def process_result(result):

    candidate = create_candidate(
        result
    )

    print()
    print("-" * 70)
    print("MATCH FOUND")
    print("-" * 70)

    print(
        "Platform:",
        candidate["platform"]
    )

    print(
        "Category:",
        candidate["category"]
    )

    print(
        "Keyword:",
        candidate["keyword"]
    )

    print(
        "Profession:",
        candidate["profession"]
        or "Not detected"
    )

    print(
        "Public URL:",
        candidate["url"]
    )

    print(
        "Score:",
        candidate["score"]
    )

    print("-" * 70)

    send_to_google(
        candidate
    )


# =========================================================
# MAIN RADAR
# =========================================================

def run_radar():

    print()
    print("=" * 70)
    print("RSD JOB SEEKER RADAR")
    print("=" * 70)

    print(
        "Started:",
        datetime.now().isoformat()
    )


    total_searches = 0

    total_matches = 0


    for category in KEYWORDS:

        print()
        print(
            f"### {category}"
        )


        for platform, domain in PLATFORMS.items():

            total_searches += 1

            results = google_search(

                platform,

                domain,

                category

            )


            for result in results:

                total_matches += 1

                process_result(
                    result
                )

                # Small delay between
                # Apps Script submissions

                time.sleep(1)


            # Delay between searches

            time.sleep(5)


    print()
    print("=" * 70)
    print("RADAR COMPLETE")
    print("=" * 70)

    print(
        f"Searches: "
        f"{total_searches}"
    )

    print(
        f"Results processed: "
        f"{total_matches}"
    )

    print(
        "Finished:",
        datetime.now().isoformat()
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    run_radar()
