import requests
from datetime import datetime


APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbzZvszdkfDv-ELPj_Hu1VGSdIGhBEATnQP0m2KHx6cDxjXMCXFOoaH0yOh5GzHVj8hk"
    "/exec"
)


def send_to_google(candidate):

    try:

        print("Sending candidate to Google Apps Script...")

        response = requests.post(
            APPS_SCRIPT_URL,
            json=candidate,
            timeout=30,
            allow_redirects=True
        )

        print("--------------------------------")
        print(
            f"Google HTTP Status: "
            f"{response.status_code}"
        )

        print(
            f"Final URL: "
            f"{response.url}"
        )

        print("Google Response:")
        print(response.text)

        print("--------------------------------")

        return response


    except requests.RequestException as error:

        print("--------------------------------")
        print("CONNECTION ERROR")
        print(error)
        print("--------------------------------")

        return None


def test_connection():

    candidate = {

        "platform": "TEST",

        "name": "TEST CANDIDATE",

        "email": "test@example.com",

        "phone": "09170000000",

        "profession": "CSR",

        "resume_url": "",

        "url": "https://example.com/test",

        "text": "BPO applicant looking for a job",

        "score": 50,

        "found_at":
            datetime.now().isoformat()

    }


    print("TEST CANDIDATE")
    print(candidate)

    send_to_google(candidate)


if __name__ == "__main__":

    test_connection()
