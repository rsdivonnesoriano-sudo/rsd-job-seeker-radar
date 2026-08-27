import requests
from datetime import datetime

APPS_SCRIPT_URL = (
    "https://script.google.com/macros/s/"
    "AKfycbzZvszdkfDv-ELPj_Hu1VGSdIGhBEATnQP0m2KHx6cDxjXMCXFOoaH0yOh5GzHVj8hk"
    "/exec"
)


def send_to_google(candidate):
    try:
        response = requests.post(
            APPS_SCRIPT_URL,
            json=candidate,
            timeout=30
        )

        print(f"Google response: {response.status_code}")
        print(response.text)

        return response

    except requests.RequestException as error:
        print(f"ERROR: {error}")
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
        "found_at": datetime.now().isoformat()
    }

    send_to_google(candidate)


if __name__ == "__main__":
    test_connection()
