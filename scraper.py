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
# SEARCH ENGINES / PUBLIC SOURCES
# =========================================================

SEARCH_URL = "https://www.google.com/search?q={}"


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
# SESSION
# =========================================================

session = requests.Session()

session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/131.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9"
})


# =========================================================
# TEXT CLEANER
# =========================================================

def clean_text(value):

    if not value:
        return ""

    return " ".join(
        str(value).split()
    ).strip()


# =========================================================
# SCORE
# =========================================================

def calculate_score(text):

    text = text.lower()

    score = 0

    for category in KEYWORDS:

        for keyword in KEYWORDS[category]:

            if keyword.lower() in text:

                if (
                    "looking for a job" in keyword.lower()
                    or
                    "looking for work" in keyword.lower()
                    or
                    "seeking employment" in keyword.lower()
                ):

                    score += 30

                else:

                    score += 15

    return min(score, 100)


# =========================================================
# DETECT PROFESSION
# =========================================================

def detect_profession(text):

    text = text.lower()

    if "pharmacist" in text:
        return "Pharmacist"

    if "phrn" in text:
        return "PHRN"

    if "usrn" in text:
        return "USRN"

    if "registered nurse" in text:
        return "Registered Nurse"

    if "call center" in text:
        return "Call Center Agent"

    if "bpo" in text:
        return "BPO Agent"

    return ""


# =========================================================
# SEARCH PUBLIC RESULTS
# =========================================================

def search_public_results(
    platform,
    site,
    keyword,
    category
):

    query = (
        f'site:{site} '
        f'"{keyword}" '
        f'Philippines'
    )

    encoded_query = quote(query)

    url = SEARCH_URL.format(
        encoded_query
    )

    print()
    print("=" * 70)
    print("SEARCHING")
    print("=" * 70)
    print(f"Platform : {platform}")
    print(f"Category : {category}")
    print(f"Keyword  : {keyword}")

    try:

        response = session.get(
            url,
            timeout=30
        )

        print(
            f"Search status: "
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


        # Google result containers
        for item in soup.select("div.MjjYud"):

            link_element = item.select_one(
                "a"
            )

            if not link_element:

                continue


            href = (
                link_element.get("href")
                or ""
            )


            if not href:

                continue


            if not is_valid_platform_url(
                href,
                site
            ):

                continue


            title_element = item.select_one(
                "h3"
            )


            if not title_element:

                continue


            title = clean_text(
                title_element.get_text(
                    " ",
                    strip=True
                )
            )


            snippet_element = item.select_one(
                ".VwiC3b"
            )


            snippet = ""

            if snippet_element:

                snippet = clean_text(
                    snippet_element.get_text(
                        " ",
                        strip=True
                    )
                )


            combined = (
                f"{title} {snippet}"
            )


            if keyword.lower() not in combined.lower():

                continue


            results.append({

                "title":
                    title,

                "url":
                    href,

                "snippet":
                    snippet,

                "platform":
                    platform,

                "category":
                    category,

                "keyword":
                    keyword

            })


        print(
            f"Matching public results: "
            f"{len(results)}"
        )

        return results


    except requests.RequestException as error:

        print(
            f"Search error: {error}"
        )

        return []


# =========================================================
# VALIDATE PLATFORM URL
# =========================================================

def is_valid_platform_url(
    url,
    site
):

    try:

        parsed = urlparse(url)

        hostname = (
            parsed.netloc
            .lower()
        )

        return site in hostname

    except Exception:

        return False


# =========================================================
# CREATE CANDIDATE
# =========================================================

def create_candidate(result):

    title = result["title"]

    snippet = result["snippet"]

    platform = result["platform"]

    category = result["category"]

    keyword = result["keyword"]

    source_url = result["url"]


    combined_text = (
        f"{title} {snippet}"
    )


    profession = detect_profession(
        combined_text
    )


    score = calculate_score(
        combined_text
    )


    candidate = {

        "platform":
            platform,

        "name":
            title,

        "email":
            "",

        "phone":
            "",

        "profession":
            profession,

        "resume_url":
            "",

        "url":
            source_url,

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


    return candidate


# =========================================================
# SEND TO GOOGLE
# =========================================================

def send_to_google(candidate):

    try:

        print()
        print("Sending result to Google...")

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
        f"Platform: "
        f"{candidate['platform']}"
    )

    print(
        f"Category: "
        f"{candidate['category']}"
    )

    print(
        f"Keyword: "
        f"{candidate['keyword']}"
    )

    print(
        f"Profession: "
        f"{candidate['profession'] or 'Not detected'}"
    )

    print(
        f"Public URL: "
        f"{candidate['url']}"
    )

    print(
        f"Score: "
        f"{candidate['score']}"
    )

    print("-" * 70)


    send_to_google(
        candidate
    )


# =========================================================
# RUN SEARCH
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


    search_count = 0

    result_count = 0


    for category in KEYWORDS:

        print()
        print(
            f"\n### {category}"
        )


        for keyword in KEYWORDS[category]:

            for platform, site in SEARCH_SITES.items():

                search_count += 1


                results = search_public_results(

                    platform,

                    site,

                    keyword,

                    category

                )


                for result in results:

                    result_count += 1

                    process_result(
                        result
                    )

                    time.sleep(1)


                time.sleep(3)


    print()
    print("=" * 70)
    print("RADAR COMPLETE")
    print("=" * 70)

    print(
        f"Searches: {search_count}"
    )

    print(
        f"Results processed: "
        f"{result_count}"
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
