import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import quote, urlparse
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

DDG_URL = "https://html.duckduckgo.com/html/?q={}"


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
# SESSION
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
# CLEAN
# =========================================================

def clean(text):

    if not text:
        return ""

    return " ".join(
        str(text).split()
    ).strip()


# =========================================================
# CHECK DOMAIN
# =========================================================

def is_platform_url(url, domain):

    try:

        hostname = (
            urlparse(url)
            .netloc
            .lower()
        )

        return domain in hostname

    except Exception:

        return False


# =========================================================
# FIND KEYWORD
# =========================================================

def find_keyword(text, keywords):

    lower = text.lower()

    matches = []

    for keyword in keywords:

        if keyword.lower() in lower:

            matches.append(keyword)

    if not matches:
        return ""

    # longest / most specific first
    matches.sort(
        key=len,
        reverse=True
    )

    return matches[0]


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
# SEARCH DUCKDUCKGO
# =========================================================

def search_duckduckgo(
    platform,
    domain,
    category
):

    keywords = KEYWORDS[category]

    # Instead of putting ALL exact phrases
    # into one query, use the strongest terms.

    if category == "GENERAL":

        query = (
            f'site:{domain} '
            '"looking for a job" OR '
            '"looking for work" OR '
            '"open to work"'
        )

    elif category == "HEALTHCARE":

        query = (
            f'site:{domain} '
            '(pharmacist OR '
            '"registered nurse" OR '
            'PHRN OR USRN) '
            '(job OR work OR employment)'
        )

    else:

        query = (
            f'site:{domain} '
            '(BPO OR '
            '"call center") '
            '(job OR work OR applicant)'
        )


    url = DDG_URL.format(
        quote(query)
    )


    print()
    print("=" * 70)
    print("SEARCH")
    print("=" * 70)

    print(
        "Platform:",
        platform
    )

    print(
        "Category:",
        category
    )

    print(
        "Query:",
        query
    )


    try:

        response = session.get(
            url,
            timeout=30
        )


        print(
            "Search status:",
            response.status_code
        )


        if response.status_code != 200:

            print(
                "Search failed."
            )

            return []


        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )


        results = []


        # =================================================
        # DUCKDUCKGO RESULT BLOCKS
        # =================================================

        result_blocks = soup.select(
            ".result"
        )


        print(
            "Raw result blocks:",
            len(result_blocks)
        )


        for block in result_blocks:

            title_element = block.select_one(
                ".result__title"
            )

            link_element = block.select_one(
                ".result__a"
            )

            snippet_element = block.select_one(
                ".result__snippet"
            )


            if not link_element:
                continue


            title = clean(
                link_element.get_text(
                    " ",
                    strip=True
                )
            )


            result_url = (
                link_element.get(
                    "href",
                    ""
                )
            )


            snippet = ""

            if snippet_element:

                snippet = clean(
                    snippet_element.get_text(
                        " ",
                        strip=True
                    )
                )


            if not result_url:
                continue


            if not is_platform_url(
                result_url,
                domain
            ):

                continue


            combined = (
                title +
                " " +
                snippet
            )


            matched_keyword = find_keyword(
                combined,
                keywords
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


        # =================================================
        # REMOVE DUPLICATES
        # =================================================

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
            "Matching public results:",
            len(unique)
        )


        return unique


    except Exception as error:

        print(
            "SEARCH ERROR:",
            error
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
# SEND TO APPS SCRIPT
# =========================================================

def send_to_google(candidate):

    try:

        print(
            "Sending to Google Apps Script..."
        )


        response = session.post(

            APPS_SCRIPT_URL,

            json=candidate,

            timeout=30,

            allow_redirects=True

        )


        print(
            "Google status:",
            response.status_code
        )

        print(
            "Google response:",
            response.text
        )


        return response


    except requests.RequestException as error:

        print(
            "GOOGLE ERROR:",
            error
        )

        return None


# =========================================================
# PROCESS
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
# MAIN
# =========================================================

def run_radar():

    print()
    print("=" * 70)
    print("RSD JOB SEEKER RADAR")
    print("=" * 70)


    searches = 0

    matches = 0


    for category in KEYWORDS:

        print()
        print(
            "###",
            category
        )


        for platform, domain in PLATFORMS.items():

            searches += 1


            results = search_duckduckgo(

                platform,

                domain,

                category

            )


            for result in results:

                matches += 1

                process_result(
                    result
                )

                time.sleep(2)


            # Prevent aggressive requests

            time.sleep(8)


    print()
    print("=" * 70)
    print("RADAR COMPLETE")
    print("=" * 70)

    print(
        "Searches:",
        searches
    )

    print(
        "Results processed:",
        matches
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
