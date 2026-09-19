import csv
import requests
from bs4 import BeautifulSoup

URL = "https://realpython.github.io/fake-jobs/"
OUTPUT_FILE = "jobs.csv"
FIELDNAMES = ["title", "company", "location", "url"]


def fetch_page(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.text


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


def parse_jobs(html):
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find(id="ResultsContainer")
    if results is None:
        return []

    jobs = []
    for card in results.find_all("div", class_="card"):
        jobs.append({
            "title": get_text(card, "h2", "title"),
            "company": get_text(card, "h3", "company"),
            "location": get_text(card, "p", "location"),
            "url": get_apply_link(card),
        })
    return jobs


def save_to_csv(jobs, filename):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(jobs)


def main():
    html = fetch_page(URL)
    jobs = parse_jobs(html)
    save_to_csv(jobs, OUTPUT_FILE)
    print(f"Scraped {len(jobs)} jobs to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()