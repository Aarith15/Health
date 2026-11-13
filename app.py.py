from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from html import escape

# STARTER DATABASE: these are example entries, not a complete medical database.
DATABASE = [
    {
        "phrases": [
            "antibiotics cure the common cold",
            "antibiotics can cure a common cold"
        ],
        "verdict": "FALSE",
        "explanation": "Antibiotics treat certain bacterial infections. They do not treat viruses that cause the common cold.",
        "sources": [
            ("CDC - Common Cold", "https://www.cdc.gov/common-cold/about/index.html"),
            ("NHS - Antibiotics", "https://www.nhs.uk/conditions/antibiotics/")
        ]
    },
    {
        "phrases": [
            "vaccines cause autism",
            "vaccination causes autism"
        ],
        "verdict": "FALSE",
        "explanation": "Large studies have found no causal link between vaccines and autism.",
        "sources": [
            ("CDC - Autism and Vaccines", "https://www.cdc.gov/vaccine-safety/about/autism.html"),
            ("WHO - Vaccines and immunization", "https://www.who.int/health-topics/vaccines-and-immunization")
        ]
    },
    {
        "phrases": [
            "vaccines help prevent infectious diseases",
            "vaccines protect against infectious diseases"
        ],
        "verdict": "TRUE",
        "explanation": "Vaccines help the immune system recognize and protect against specific infectious diseases.",
        "sources": [
            ("WHO - Vaccines and immunization", "https://www.who.int/health-topics/vaccines-and-immunization"),
            ("CDC - Benefits of Vaccination", "https://www.cdc.gov/vaccines/basics/vaccine-preventable-diseases.html")
        ]
    },
    {
        "phrases": [
            "cancer is contagious",
            "cancer spreads from person to person"
        ],
        "verdict": "FALSE",
        "explanation": "Cancer itself is not contagious and does not spread from one person to another through ordinary contact.",
        "sources": [
            ("National Cancer Institute - Common Cancer Myths", "https://www.cancer.gov/about-cancer/causes-prevention/risk/myths"),
            ("American Cancer Society - Is Cancer Contagious?", "https://www.cancer.org/cancer/understanding-cancer/is-cancer-contagious.html")
        ]
    },
    {
        "phrases": [
            "washing hands means vaccines are unnecessary",
            "handwashing makes vaccines unnecessary"
        ],
        "verdict": "FALSE",
        "explanation": "Handwashing helps reduce the spread of germs, but it does not replace vaccination. These are different ways to help prevent illness.",
        "sources": [
            ("CDC - About Handwashing", "https://www.cdc.gov/clean-hands/about/index.html"),
            ("WHO - Vaccines and immunization", "https://www.who.int/health-topics/vaccines-and-immunization")
        ]
    }
]


def normalize(text):
    return " ".join(text.lower().strip().rstrip(" .!?").split())


def make_result(claim):
    cleaned = normalize(claim)
    match = None

    for item in DATABASE:
        if cleaned in [normalize(phrase) for phrase in item["phrases"]]:
            match = item
            break

    if match is None:
        return (
            '<section class="result">'
            '<div class="small-heading">RESULT</div>'
            '<h2 class="verdict unverified">UNVERIFIED</h2>'
            '<p>This claim is not in the prototype database, so this tool cannot verify it.</p>'
            '<p>Do not treat an unverified claim as true or false. Check with a qualified healthcare professional and reliable sources.</p>'
            '</section>'
        )

    links = "".join(
        '<li><a href="' + escape(url, quote=True) + '" target="_blank" rel="noopener noreferrer">'
        + escape(title) + '</a></li>'
        for title, url in match["sources"]
    )
    verdict_class = match["verdict"].lower()

    return (
        '<section class="result">'
        '<div class="small-heading">RESULT</div>'
        '<h2 class="verdict ' + verdict_class + '">' + match["verdict"] + '</h2>'
        '<p><strong>Explanation:</strong> ' + escape(match["explanation"]) + '</p>'
        '<p><strong>Sources:</strong></p><ul>' + links + '</ul>'
        '<p class="note">This is a small educational prototype using exact phrase matching. '
        'It may not recognize differently worded claims.</p>'
        '</section>'
    )


HTML_START = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>HealthCheck AI - Health Rumour Fact Checker</title>
<style>
* { box-sizing: border-box; }
body { font-family: Arial, sans-serif; background: #f0f7f2; color: #24352a; margin: 0; padding: 24px 14px; }
.container { max-width: 700px; margin: 24px auto; background: white; padding: 30px; border-radius: 16px; box-shadow: 0 4px 18px #00000012; }
h1 { color: #198754; text-align: center; margin-bottom: 6px; }
.subtitle { text-align: center; color: #617166; margin-top: 0; }
label { display: block; font-weight: bold; margin: 24px 0 9px; }
textarea { width: 100%; min-height: 115px; padding: 13px; border: 1px solid #b9c9bd; border-radius: 9px; font: inherit; resize: vertical; }
button { width: 100%; padding: 14px; margin-top: 12px; background: #198754; color: white; border: 0; border-radius: 9px; font-size: 16px; font-weight: bold; cursor: pointer; }
button:hover { background: #146c43; }
.result { margin-top: 25px; padding: 20px; background: #f5faf6; border: 1px solid #dcebe0; border-radius: 12px; overflow-wrap: anywhere; }
.small-heading { color: #617166; font-size: 12px; letter-spacing: 1px; }
.verdict { margin: 4px 0 18px; }
.true { color: #16803c; }
.false { color: #c0392b; }
.unverified { color: #a66b00; }
li { margin: 9px 0; }
a { color: #1769aa; }
.note { margin-top: 20px; padding-top: 12px; border-top: 1px solid #dcebe0; color: #647269; font-size: 13px; }
.safety { text-align: center; color: #647269; font-size: 14px; margin-top: 24px; }
.examples { color: #647269; font-size: 13px; line-height: 1.6; }
</style>
</head>
<body>
<main class="container">
<h1>HealthCheck AI</h1>
<p class="subtitle">Health Rumour Fact Checker</p>
<p>Enter a health claim below. The prototype compares it with its small example database.</p>
<form action="/check" method="get">
<label for="claim">Health claim</label>
<textarea id="claim" name="claim" placeholder="Example: Antibiotics cure the common cold" required>CLAIM_VALUE</textarea>
<button type="submit">Check Claim</button>
</form>
RESULT_PLACEHOLDER
<p class="examples"><strong>Try an example:</strong><br>
Antibiotics cure the common cold<br>
Vaccines cause autism<br>
Cancer is contagious</p>
<div class="safety">Always ask a doctor or qualified healthcare professional.</div>
</main>
</body>
</html>
"""


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        address = urlparse(self.path)
        result = ""
        claim_value = ""

        if address.path == "/check":
            values = parse_qs(address.query)
            claim = values.get("claim", [""])[0].strip()
            claim_value = escape(claim, quote=True)
            if claim:
                result = make_result(claim)

        page = HTML_START.replace("RESULT_PLACEHOLDER", result)
        page = page.replace("CLAIM_VALUE", claim_value)

        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(page.encode("utf-8"))

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 5000), HealthCheckHandler)
    print("HealthCheck AI is running at http://127.0.0.1:5000")
    print("Keep this window open while using the website. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Server stopped.")
        server.server_close()
