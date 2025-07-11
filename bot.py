from flask import Flask, request, jsonify
import requests, re
from bs4 import BeautifulSoup

app = Flask(__name__)

def extract_code(html):
    """Trích mã 6 hoặc 8 số từ HTML."""
    match = re.search(r"\b(\d{6}|\d{8})\b", html)
    return match.group(1) if match else None

def check_fb(email):
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Mobile Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Referer": "https://m.facebook.com/login/identify/?ctx=recover",
        "Connection": "keep-alive"
    })

    try:
        res1 = s.get("https://m.facebook.com/login/identify/?ctx=recover", timeout=10)
        soup1 = BeautifulSoup(res1.text, "html.parser")
        lsd = soup1.find("input", {"name": "lsd"})
        jazoest = soup1.find("input", {"name": "jazoest"})

        if not lsd or not jazoest:
            return {"status": "error", "reason": "tokens missing"}

        payload = {
            "lsd": lsd["value"],
            "jazoest": jazoest["value"],
            "email": email,
            "did_submit": "Search"
        }

        res2 = s.post("https://m.facebook.com/login/identify/?ctx=recover", data=payload, timeout=10)
        soup2 = BeautifulSoup(res2.text, "html.parser")
        form = soup2.find("form")

        if not form or "hash=" not in str(form.get("action", "")):
            return {"status": "not_linked", "code": None}

        res3 = s.get("https://m.facebook.com" + form.get("action"), timeout=10)
        code = extract_code(res3.text)

        return {"status": "linked", "code": code}

    except Exception as e:
        return {"status": "error", "reason": str(e)}

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "✅ FB Email Checker API đang hoạt động!"})

@app.route("/check", methods=["POST"])
def check():
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "missing email"}), 400

    email = data["email"]
    result = check_fb(email)
    result["email"] = email
    return jsonify(result)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
