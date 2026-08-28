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
# SEARCH SETTINGS
# =========================================================

SEARCH_SITES = {
    "Facebook": "facebook.com",
    "LinkedIn": "linkedin.com"
}


# =========================================================
# JOB SEEKER KEYWORDS
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
        "Chrome/131.0 Safari/537.36",

    "Accept":
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8",

    "Accept-Language":
        "en-US,en;q=0.9"

})


# =========================================================
# SEARCH DUCKDUCKGO
# =========================================================

def search_public_web(keyword, site):

    query = (
        f'site:{site} '
        f'"{keyword}" '
        f'Philippines'
    )

    search_url = (
        "https://html.duckduckgo.com/html/?q="
        + quote(query)
    )

    print()
    print("=" * 70)
    print("SEARCH")
    print("=" * 70)
    print(f"Platform : {site}")
    print(f"Keyword  : {keyword}")
    print(f"Query    : {query}")

    try:

        response = session.get(
            search_url,
            timeout=30
        )

        print(
            f"Search HTTP Status: "
            f"{response.status_code}"
        )

        if response.status_code != 200:

            print(
                "Search request failed."
            )

            return []

        soup = BeautifulSoup(
            response.text,
            "html.parser"
        )

        results = []

        for result in soup.select(
            ".result"
        ):

            title_element = result.select_one(
                ".result__title"
            )

            link_element = result.select_one(
                ".result__a"
            )

            snippet_element = result.select_one(
                ".result__snippet"
            )

            if not link_element:

                continue

            title = clean_text(
                link_element.get_text(
                    " ",
                    strip=True
                )
            )

            url = (
                link_element.get("href")
                or ""
            )

            snippet = ""

            if snippet_element:

                snippet = clean_text(
                    snippet_element.get_text(
                        " ",
                        strip=True
                    )
                )

            if not url:

                continue

            if not is_allowed_social_url(
                url,
                site
            ):

                continue

            results.append({

                "title": title,

                "url": url,

                "snippet": snippet

            })


        print(
            f"Public results found: "
            f"{len(results)}"
        )

        return results


    except requests.RequestException as error:

        print(
            f"Search error: {error}"
        )

        return []


# =========================================================
# CHECK SOCIAL URL
# =========================================================

def is_allowed_social_url(url, site):

    try:

        hostname = (
            urlparse(url)
            .netloc
            .lower()
        )

        return (
            site in hostname
        )

    except Exception:

        return False


# =========================================================
# CHECK KEYWORD
# =========================================================

def find_matching_keyword(
    title,
    snippet,
    keyword
):

    combined = (
        f"{title} {snippet}"
    ).lower()

    return (
        keyword.lower()
        in combined
    )


# =========================================================
# FIND RESUME LINK
# =========================================================

def find_resume_url(text):

    if not text:

        return ""

    lower = text.lower()

    resume_terms = [

        ".pdf",
        ".doc",
        ".docx",
        "resume",
        "curriculum vitae",
        "cv"

    ]

    for term in resume_terms:

        if term in lower:

            return ""

    return ""


# =========================================================
# EXTRACT NAME FROM TITLE
# =========================================================

def extract_name(title):

    if not title:

        return ""

    separators = [

        " - ",
        " | ",
        " — ",
        " – "

    ]

    name = title

    for separator in separators:

        if separator in name:

            name = name.split(
                separator
            )[0]

            break

    name = clean_text(name)

    return name[:150]


# =========================================================
# EXTRACT PROFESSION
# =========================================================

def detect_profession(
    text,
    category
):

    lower = text.lower()

    if category == "HEALTHCARE":

        if (
            "pharmacist"
            in lower
        ):

            return "Pharmacist"

        if (
            "phrn"
            in lower
        ):

            return "PHRN"

        if (
            "usrn"
            in lower
        ):

            return "USRN"

        if (
            "registered nurse"
            in lower
        ):

            return "Registered Nurse"


    if category == "BPO_AGENT":

        if (
            "call center"
            in lower
            or
            "call centre"
            in lower
        ):

            return "Call Center Agent"

        if (
            "bpo"
            in lower
        ):

            return "BPO Agent"


    return ""


# =========================================================
# CALCULATE SCORE
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
# SEND TO GOOGLE
# =========================================================

def send_to_google(candidate):

    try:

        print()
        print("Sending candidate to Google...")

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
            f"Google Response: "
            f"{response.text}"
        )

        return response


    except requests.RequestException as error:

        print(
            f"Google connection error: "
            f"{error}"
        )

        return None


# =========================================================
# PROCESS SEARCH RESULT
# =========================================================

def process_result(
    result,
    platform,
    keyword,
    category
):

    title = result.get(
        "title",
        ""
    )

    url = result.get(
        "url",
        ""
    )

    snippet = result.get(
        "snippet",
        ""
    )


    combined_text = (
        f"{title} {snippet}"
    )


    if not find_matching_keyword(
        title,
        snippet,
        keyword
    ):

        return False


    name = extract_name(
        title
    )


    profession = detect_profession(
        combined_text,
        category
    )


    score = calculate_score(
        combined_text
    )


    candidate = {

        "platform":
            platform,

        "name":
            name,

        "email":
            "",

        "phone":
            "",

        "profession":
            profession,

        "resume_url":
            find_resume_url(
                combined_text
            ),

        "url":
            url,

        "text":
            combined_text,

        "score":
            score,

        "keyword":
            keyword,

        "category":
            category,

        "found_at":
            datetime.now().isoformat()

    }


    print()
    print("-" * 70)
    print("MATCH FOUND")
    print("-" * 70)

    print(
        f"Platform: {platform}"
    )

    print(
        f"Category: {category}"
    )

    print(
        f"Keyword: {keyword}"
    )

    print(
        f"Name: {name or 'Not available'}"
    )

    print(
        f"Profession: "
        f"{profession or 'Not detected'}"
    )

    print(
        f"URL: {url}"
    )

    print(
        f"Score: {score}"
    )

    print("-" * 70)


    send_to_google(
        candidate
    )

    return True


# =========================================================
# RUN ONE KEYWORD
# =========================================================

def run_keyword(
    keyword,
    category
):

    for platform, site in SEARCH_SITES.items():

        results = search_public_web(
            keyword,
            site
        )

        for result in results:

            process_result(
                result,
                platform,
                keyword,
                category
            )

            time.sleep(1)


        time.sleep(3)


# =========================================================
# MAIN RADAR
# =========================================================

def run_radar():

    print()
    print("=" * 70)
    print("RSD JOB SEEKER RADAR")
    print("=" * 70)

    print(
        f"Started: "
        f"{datetime.now().isoformat()}"
    )

    total_keywords = 0


    for category in KEYWORDS:

        print()
        print(
            f"### CATEGORY: {category}"
        )


        for keyword in KEYWORDS[category]:

            total_keywords += 1

            run_keyword(
                keyword,
                category
            )

            time.sleep(3)


    print()
    print("=" * 70)
    print("RADAR FINISHED")
    print("=" * 70)

    print(
        f"Keywords searched: "
        f"{total_keywords}"
    )

    print(
        f"Finished: "
        f"{datetime.now().isoformat()}"
    )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":

    run_radar()
