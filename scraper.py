import requests
from bs4 import BeautifulSoup

URL = "https://realpython.github.io/fake-jobs/"

response = requests.get(URL, timeout=10)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

results = soup.find(id="ResultsContainer")
cards = results.find_all("div", class_="card")

print("cards found:", len(cards))

def get_text(card, tag, class_name, default=""):
    element = card.find(tag, class_=class_name)
    if element is None:
        return default
    return element.text.strip()


def get_apply_link(card, default=""):
    link = card.find("a", string="Apply")
    if link is None:
        return default
    return link.get("href", default)


jobs = []

for card in cards:
    job = {
        "title": get_text(card, "h2", "title"),
        "company": get_text(card, "h3", "company"),
        "location": get_text(card, "p", "location"),
        "url": get_apply_link(card),
    }
    jobs.append(job)

print("jobs collected:", len(jobs))
for job in jobs[:3]:
    print(job)