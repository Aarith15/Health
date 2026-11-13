import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from html import escape


def entry(title, category, verdict, explanation, sources):
    return {
        "phrases": [title.lower()],
        "title": title,
        "category": category,
        "verdict": verdict,
        "explanation": explanation,
        "sources": sources
    }


DATABASE = [
    entry("Antibiotics cure the common cold", "Medicines", "FALSE",
          "Antibiotics treat certain bacterial infections, not viruses that cause the common cold.",
          [("CDC - Common Cold", "https://www.cdc.gov/common-cold/about/"),
           ("NHS - Antibiotics", "https://www.nhs.uk/conditions/antibiotics/")]),

    entry("Vaccines cause autism", "Vaccines", "FALSE",
          "Large studies have found no causal link between vaccines and autism.",
          [("CDC - Autism and Vaccines", "https://www.cdc.gov/vaccine-safety/about/autism.html"),
           ("WHO - Vaccines", "https://www.who.int/health-topics/vaccines-and-immunization")]),

    entry("Cold weather itself causes the common cold", "Immunity", "FALSE",
          "Common colds are caused by viruses, not simply by being in cold weather.",
          [("CDC - Common Cold", "https://www.cdc.gov/common-cold/about/"),
           ("NHS - Common Cold", "https://www.nhs.uk/conditions/common-cold/")]),

    entry("Cracking your knuckles definitely causes arthritis", "Joints", "FALSE",
          "Research has not established that habitual knuckle cracking causes arthritis.",
          [("NIAMS - Osteoarthritis", "https://www.niams.nih.gov/health-topics/osteoarthritis"),
           ("NHS - Arthritis", "https://www.nhs.uk/conditions/arthritis/")]),

    entry("Carrots give you perfect night vision", "Nutrition", "FALSE",
          "Vitamin A supports normal vision, but extra carrots do not give people superhuman night vision.",
          [("NIH - Vitamin A", "https://ods.od.nih.gov/factsheets/VitaminA-Consumer/"),
           ("WHO - Blindness and Vision Loss", "https://www.who.int/health-topics/blindness-and-vision-loss")]),

    entry("Sugar always makes children hyperactive", "Children", "FALSE",
          "Research has not consistently shown that sugar itself causes hyperactivity in children.",
          [("NHS - Sugar", "https://www.nhs.uk/live-well/eat-well/food-types/how-does-sugar-in-our-diet-affect-our-health/"),
           ("CDC - Children's Health", "https://www.cdc.gov/children-mental-health/about/")]),

    entry("HIV spreads through sharing food", "Infectious Diseases", "FALSE",
          "HIV does not spread through sharing meals, plates or ordinary social contact.",
          [("WHO - HIV", "https://www.who.int/news-room/fact-sheets/detail/hiv-aids"),
           ("CDC - HIV Transmission", "https://www.cdc.gov/hiv/causes/")]),

    entry("Malaria spreads through ordinary physical touch", "Infectious Diseases", "FALSE",
          "Malaria is mainly transmitted through bites from infected female Anopheles mosquitoes.",
          [("WHO - Malaria", "https://www.who.int/news-room/fact-sheets/detail/malaria"),
           ("CDC - Malaria", "https://www.cdc.gov/malaria/about/")]),

    entry("Dengue spreads through sharing meals", "Infectious Diseases", "FALSE",
          "Dengue is primarily transmitted through infected Aedes mosquitoes, not by sharing food.",
          [("WHO - Dengue", "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue"),
           ("CDC - Dengue", "https://www.cdc.gov/dengue/about/")]),

    entry("Tuberculosis spreads by sharing plates", "Infectious Diseases", "FALSE",
          "TB usually spreads through the air when someone with infectious TB coughs or speaks.",
          [("WHO - Tuberculosis", "https://www.who.int/news-room/fact-sheets/detail/tuberculosis"),
           ("CDC - TB", "https://www.cdc.gov/tb/about/")]),

    entry("All cancers are contagious", "Cancer", "FALSE",
          "Cancer itself is not contagious. Some infections that increase cancer risk can spread between people.",
          [("WHO - Cancer", "https://www.who.int/news-room/fact-sheets/detail/cancer"),
           ("NCI - Infectious Agents", "https://www.cancer.gov/about-cancer/causes-prevention/risk/infectious-agents")]),

    entry("Diabetes is caused only by eating sugar", "Diabetes", "FALSE",
          "Diabetes has several causes involving genetics, insulin production and insulin resistance.",
          [("WHO - Diabetes", "https://www.who.int/news-room/fact-sheets/detail/diabetes"),
           ("NIDDK - Diabetes", "https://www.niddk.nih.gov/health-information/diabetes/overview")]),

    entry("People with diabetes must never eat fruit", "Diabetes", "FALSE",
          "Many people with diabetes can include whole fruit in a balanced eating plan.",
          [("American Diabetes Association - Food", "https://diabetes.org/food-nutrition"),
           ("NHS - Diabetes", "https://www.nhs.uk/conditions/type-2-diabetes/")]),

    entry("Everyone must drink exactly eight glasses of water daily", "Hydration", "FALSE",
          "Water needs vary with activity, climate, age, diet and individual health.",
          [("NHS - Water and Drinks", "https://www.nhs.uk/live-well/eat-well/water-drinks-nutrition/"),
           ("CDC - Water and Health", "https://www.cdc.gov/healthy-weight-growth/water-healthy-drinks/")]),

    entry("Microwaving food makes it radioactive", "Food Safety", "FALSE",
          "Microwave ovens use non-ionizing radiation and do not make food radioactive.",
          [("FDA - Microwave Oven Radiation", "https://www.fda.gov/radiation-emitting-products/home-business-and-entertainment-products/microwave-oven-radiation"),
           ("WHO - Electromagnetic Fields", "https://www.who.int/health-topics/electromagnetic-fields")]),

    entry("All bacteria are harmful", "Microbiology", "FALSE",
          "Many bacteria are harmless or helpful, including bacteria that support digestion.",
          [("NIH - Human Microbiome", "https://www.nih.gov/research-training/medical-research-initiatives/human-microbiome-project"),
           ("NCCIH - Probiotics", "https://www.nccih.nih.gov/health/probiotics-what-you-need-to-know")]),

    entry("Handwashing with soap helps prevent infections", "Hygiene", "TRUE",
          "Washing hands with soap and water helps remove germs and reduce the spread of infections.",
          [("WHO - Hand Hygiene", "https://www.who.int/health-topics/hand-hygiene"),
           ("CDC - Handwashing", "https://www.cdc.gov/clean-hands/about/")]),

    entry("Mosquitoes can breed in stagnant water", "Prevention", "TRUE",
          "Many disease-spreading mosquitoes lay eggs in standing water.",
          [("WHO - Vector-borne Diseases", "https://www.who.int/news-room/fact-sheets/detail/vector-borne-diseases"),
           ("CDC - Mosquitoes", "https://www.cdc.gov/mosquitoes/about/")]),

    entry("Sharing contaminated needles can transmit HIV", "Infectious Diseases", "TRUE",
          "Sharing contaminated needles can transmit HIV and other blood-borne infections.",
          [("WHO - HIV", "https://www.who.int/news-room/fact-sheets/detail/hiv-aids"),
           ("CDC - HIV Causes", "https://www.cdc.gov/hiv/causes/")]),

    entry("Vitamin C prevents every common cold", "Nutrition", "FALSE",
          "Vitamin C does not reliably prevent colds in the general population.",
          [("NIH - Vitamin C", "https://ods.od.nih.gov/factsheets/VitaminC-Consumer/"),
           ("NHS - Vitamin C", "https://www.nhs.uk/conditions/vitamins-and-minerals/vitamin-c/")]),

    entry("A balanced diet supports good health", "Nutrition", "TRUE",
          "A varied balanced diet helps provide nutrients needed for normal body functions.",
          [("WHO - Healthy Diet", "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"),
           ("NHS - Healthy Eating", "https://www.nhs.uk/live-well/eat-well/")]),

    entry("Smoking increases the risk of lung cancer", "Cancer", "TRUE",
          "Tobacco smoking is a major risk factor for lung cancer and several other diseases.",
          [("WHO - Tobacco", "https://www.who.int/news-room/fact-sheets/detail/tobacco"),
           ("NCI - Tobacco", "https://www.cancer.gov/about-cancer/causes-prevention/risk/tobacco")]),

    entry("Sunlight helps the body produce vitamin D", "Vitamins", "TRUE",
          "Skin can produce vitamin D after sunlight exposure, although excessive UV exposure is harmful.",
          [("NIH - Vitamin D", "https://ods.od.nih.gov/factsheets/VitaminD-Consumer/"),
           ("WHO - Ultraviolet Radiation", "https://www.who.int/news-room/fact-sheets/detail/ultraviolet-radiation")]),

    entry("Everyone needs vitamin supplements", "Vitamins", "FALSE",
          "Not everyone needs supplements. Requirements depend on diet and individual health.",
          [("NIH - Dietary Supplements", "https://ods.od.nih.gov/HealthInformation/ODS_Frequently_Asked_Questions.aspx"),
           ("NHS - Vitamins", "https://www.nhs.uk/conditions/vitamins-and-minerals/")]),

    entry("Regular physical activity supports heart health", "Fitness", "TRUE",
          "Regular physical activity supports cardiovascular health and general wellbeing.",
          [("WHO - Physical Activity", "https://www.who.int/news-room/fact-sheets/detail/physical-activity"),
           ("CDC - Physical Activity", "https://www.cdc.gov/physical-activity-basics/")]),

    entry("Sleep is important for good health", "Sleep", "TRUE",
          "Adequate sleep supports brain function, mood, growth and general health.",
          [("CDC - Sleep", "https://www.cdc.gov/sleep/about/"),
           ("NHLBI - Sleep", "https://www.nhlbi.nih.gov/health/sleep")]),

    entry("Unsafe drinking water can spread disease", "Water Safety", "TRUE",
          "Unsafe drinking water can carry germs and chemicals that cause illness.",
          [("WHO - Drinking Water", "https://www.who.int/news-room/fact-sheets/detail/drinking-water"),
           ("CDC - Drinking Water", "https://www.cdc.gov/drinking-water/about/")]),

    entry("Rabies can spread through bites from infected animals", "Infectious Diseases", "TRUE",
          "Rabies can spread through the saliva of infected animals, usually through bites. Possible exposure needs urgent medical assessment.",
          [("WHO - Rabies", "https://www.who.int/news-room/fact-sheets/detail/rabies"),
           ("CDC - Rabies", "https://www.cdc.gov/rabies/about/")]),

    entry("Measles is highly contagious", "Infectious Diseases", "TRUE",
          "Measles spreads very easily through the air. Vaccination helps prevent it.",
          [("WHO - Measles", "https://www.who.int/news-room/fact-sheets/detail/measles"),
           ("CDC - Measles", "https://www.cdc.gov/measles/about/")]),

    entry("Polio can cause paralysis", "Infectious Diseases", "TRUE",
          "Poliovirus can affect the nervous system and cause paralysis in some cases.",
          [("WHO - Poliomyelitis", "https://www.who.int/news-room/fact-sheets/detail/poliomyelitis"),
           ("CDC - Polio", "https://www.cdc.gov/polio/about/")]),

    entry("Too much ultraviolet radiation can damage skin", "Skin Health", "TRUE",
          "Excessive UV exposure can damage skin and increase the risk of skin cancer.",
          [("WHO - UV Radiation", "https://www.who.int/news-room/fact-sheets/detail/ultraviolet-radiation"),
           ("NCI - Sunlight", "https://www.cancer.gov/about-cancer/causes-prevention/risk/sunlight")]),

    entry("Mental health is part of overall health", "Mental Health", "TRUE",
          "Mental wellbeing is an important part of health and deserves care and support.",
          [("WHO - Mental Health", "https://www.who.int/health-topics/mental-health"),
           ("NIMH - Mental Health Information", "https://www.nimh.nih.gov/health")]),

    entry("High blood pressure can have no obvious symptoms", "Heart Health", "TRUE",
          "Hypertension often has no noticeable symptoms, which is why checking blood pressure matters.",
          [("WHO - Hypertension", "https://www.who.int/news-room/fact-sheets/detail/hypertension"),
           ("CDC - High Blood Pressure", "https://www.cdc.gov/high-blood-pressure/about/")]),

    entry("All fats are unhealthy", "Nutrition", "FALSE",
          "Unsaturated fats can be part of a healthy diet. The type and amount of fat matter.",
          [("WHO - Healthy Diet", "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"),
           ("NHS - Different Fats", "https://www.nhs.uk/live-well/eat-well/food-types/different-fats-nutrition/")]),

    entry("Eating too much salt can raise blood pressure", "Heart Health", "TRUE",
          "High sodium intake can contribute to increased blood pressure.",
          [("WHO - Salt Reduction", "https://www.who.int/news-room/fact-sheets/detail/salt-reduction"),
           ("CDC - Sodium", "https://www.cdc.gov/salt/about/")]),

    entry("Antibiotic resistance is a public health problem", "Medicines", "TRUE",
          "Bacteria can become resistant to medicines, making some infections harder to treat.",
          [("WHO - Antimicrobial Resistance", "https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance"),
           ("CDC - Antimicrobial Resistance", "https://www.cdc.gov/antimicrobial-resistance/about/")]),

    entry("Well-fitting masks can reduce exposure to respiratory particles", "Prevention", "TRUE",
          "Well-fitting masks can reduce exposure to infectious respiratory particles, depending on the setting and mask.",
          [("CDC - Masks", "https://www.cdc.gov/respiratory-viruses/prevention/masks.html"),
           ("WHO - Respiratory Infections", "https://www.who.int/health-topics/coronavirus")]),

    entry("Vaccination helps protect against infectious diseases", "Vaccines", "TRUE",
          "Vaccines train the immune system to recognize specific germs and help prevent serious illness.",
          [("WHO - Vaccines", "https://www.who.int/health-topics/vaccines-and-immunization"),
           ("CDC - Vaccines", "https://www.cdc.gov/vaccines/basics/")]),

    entry("Every fever is dangerous", "General Health", "FALSE",
          "Fever is often part of the body's response to infection. Its significance depends on age, symptoms and circumstances.",
          [("NHS - Fever", "https://www.nhs.uk/conditions/fever-in-adults/"),
           ("MedlinePlus - Fever", "https://medlineplus.gov/fever.html")]),

    entry("All natural products are safe", "Health Products", "FALSE",
          "Natural substances can still have side effects, interact with medicines or be unsafe.",
          [("NCCIH - Know the Science", "https://www.nccih.nih.gov/health/know-science"),
           ("FDA - Dietary Supplements", "https://www.fda.gov/consumers/consumer-updates/fda-101-dietary-supplements")]),

    entry("Brushing teeth helps prevent tooth decay", "Oral Health", "TRUE",
          "Brushing with fluoride toothpaste helps remove plaque and prevent tooth decay.",
          [("WHO - Oral Health", "https://www.who.int/news-room/fact-sheets/detail/oral-health"),
           ("NHS - Clean Teeth", "https://www.nhs.uk/live-well/healthy-teeth-and-gums/how-to-keep-your-teeth-clean/")]),

    entry("Hand sanitizer is always better than soap and water", "Hygiene", "FALSE",
          "Soap and water are preferred in many situations, especially when hands are visibly dirty. Sanitizer is useful in other situations.",
          [("CDC - Hand Sanitizer", "https://www.cdc.gov/clean-hands/about/hand-sanitizer.html"),
           ("WHO - Hand Hygiene", "https://www.who.int/health-topics/hand-hygiene")]),

    entry("All headaches mean a serious illness", "General Health", "FALSE",
          "Many headaches have common causes, but sudden, severe or unusual symptoms need medical assessment.",
          [("NHS - Headaches", "https://www.nhs.uk/conditions/headaches/"),
           ("MedlinePlus - Headache", "https://medlineplus.gov/headache.html")]),

    entry("Eating a variety of foods helps provide different nutrients", "Nutrition", "TRUE",
          "Eating a variety of foods can help provide a broad range of essential nutrients.",
          [("WHO - Healthy Diet", "https://www.who.int/news-room/fact-sheets/detail/healthy-diet"),
           ("NHS - Healthy Eating", "https://www.nhs.uk/live-well/eat-well/")]),

    entry("A common cold can spread from an infected person", "Infectious Diseases", "TRUE",
          "Cold viruses can spread through respiratory particles and contaminated hands or surfaces.",
          [("CDC - Common Cold", "https://www.cdc.gov/common-cold/about/"),
           ("NHS - Common Cold", "https://www.nhs.uk/conditions/common-cold/")]),

    entry("Infected Aedes mosquitoes can transmit dengue", "Infectious Diseases", "TRUE",
          "Infected Aedes mosquitoes can transmit dengue virus to people.",
          [("WHO - Dengue", "https://www.who.int/news-room/fact-sheets/detail/dengue-and-severe-dengue"),
           ("CDC - Dengue", "https://www.cdc.gov/dengue/about/")]),

    entry("Physical activity can support mental wellbeing", "Mental Health", "TRUE",
          "Physical activity can support mental wellbeing as well as physical health.",
          [("WHO - Physical Activity", "https://www.who.int/news-room/fact-sheets/detail/physical-activity"),
           ("CDC - Physical Activity", "https://www.cdc.gov/physical-activity-basics/")]),

    entry("All people need exactly the same amount of sleep", "Sleep", "FALSE",
          "Sleep needs vary with age and individual factors.",
          [("CDC - Sleep", "https://www.cdc.gov/sleep/about/"),
           ("NHLBI - Sleep", "https://www.nhlbi.nih.gov/health/sleep")]),

    entry("Clean drinking water is important for health", "Water Safety", "TRUE",
          "Safe drinking water supports health and helps prevent waterborne diseases.",
          [("WHO - Drinking Water", "https://www.who.int/news-room/fact-sheets/detail/drinking-water"),
           ("CDC - Drinking Water", "https://www.cdc.gov/drinking-water/about/")]),

    entry("Sunburn is a sign of skin damage", "Skin Health", "TRUE",
          "Sunburn is an inflammatory response to excessive ultraviolet exposure.",
          [("WHO - UV Radiation", "https://www.who.int/news-room/fact-sheets/detail/ultraviolet-radiation"),
           ("NCI - Sunlight", "https://www.cancer.gov/about-cancer/causes-prevention/risk/sunlight")]),

    entry("A detox drink can remove all toxins from the body", "Health Claims", "FALSE",
          "There is no proven drink that removes all toxins. Organs such as the liver and kidneys process waste.",
          [("NCCIH - Detoxes and Cleanses", "https://www.nccih.nih.gov/health/detoxes-and-cleanses"),
           ("NIDDK - Kidneys", "https://www.niddk.nih.gov/health-information/kidney-disease")]),

    entry("A person can have high blood pressure without feeling ill", "Heart Health", "TRUE",
          "High blood pressure frequently has no symptoms and requires measurement to identify.",
          [("WHO - Hypertension", "https://www.who.int/news-room/fact-sheets/detail/hypertension"),
           ("CDC - High Blood Pressure", "https://www.cdc.gov/high-blood-pressure/about/")]),

    entry("Washing fruits and vegetables helps reduce contamination", "Food Safety", "TRUE",
          "Rinsing fresh produce under clean running water helps remove dirt and some germs.",
          [("FDA - Cleaning Produce", "https://www.fda.gov/consumers/consumer-updates/7-tips-cleaning-fruits-vegetables"),
           ("CDC - Food Safety", "https://www.cdc.gov/food-safety/prevention/")]),

    entry("Antibiotics should be used only when appropriately prescribed", "Medicines", "TRUE",
          "Antibiotics should be used according to qualified medical advice because unnecessary use contributes to resistance.",
          [("WHO - Antimicrobial Resistance", "https://www.who.int/news-room/fact-sheets/detail/antimicrobial-resistance"),
           ("CDC - Antibiotic Use", "https://www.cdc.gov/antibiotic-use/about/")])
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
            '<p>Do not treat an unverified claim as true or false. Check reliable sources and ask a qualified healthcare professional.</p>'
            '</section>'
        )

    links = "".join(
        '<li><a href="' + escape(url, quote=True) +
        '" target="_blank" rel="noopener noreferrer">' +
        escape(title) + '</a></li>'
        for title, url in match["sources"]
    )

    verdict_class = match["verdict"].lower()

    return (
        '<section class="result">'
        '<div class="small-heading">RESULT</div>'
        '<h2 class="verdict ' + verdict_class + '">' +
        match["verdict"] + '</h2>'
        '<p><strong>Category:</strong> ' +
        escape(match["category"]) + '</p>'
        '<p><strong>Explanation:</strong> ' +
        escape(match["explanation"]) + '</p>'
        '<p><strong>Sources:</strong></p><ul>' + links + '</ul>'
        '<p class="note">This is an educational prototype using exact phrase matching. '
        'It may not recognize differently worded claims. Its entries require review and are not a substitute for medical advice.</p>'
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
<p>Enter a health claim below. The prototype compares it with its 50-entry example database.</p>
<form action="/check" method="get">
<label for="claim">Health claim</label>
<textarea id="claim" name="claim" placeholder="Example: Antibiotics cure the common cold" required>CLAIM_VALUE</textarea>
<button type="submit">Check Claim</button>
</form>
RESULT_PLACEHOLDER
<p class="examples"><strong>Try an example:</strong><br>
Antibiotics cure the common cold<br>
Vaccines cause autism<br>
All cancers are contagious<br>
A detox drink can remove all toxins from the body</p>
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
    print("Total database entries:", len(DATABASE))

    port = int(os.environ.get("PORT", 5000))

    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)

    print("HealthCheck AI is running on port", port)
    server.serve_forever()
