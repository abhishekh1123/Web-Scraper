# Job Listings Scraper

A Python web scraper that collects job listings from the [Fake Python Jobs](https://realpython.github.io/fake-jobs/) site and exports them to a CSV file.

Project from [roadmap.sh](https://roadmap.sh/projects/job-listings-scraper).

## Features

- Fetches the listings page over HTTP with a request timeout
- Parses the HTML with Beautiful Soup and scopes each extraction to a single job card
- Extracts job title, company name, location, and the job detail page URL
- Handles missing fields gracefully — a missing element becomes an empty string instead of crashing the run
- Writes all results to `jobs.csv` with proper quoting and headers

## Requirements

- Python 3.8+
- `requests`
- `beautifulsoup4`

## Installation

```bash
git clone https://github.com/abhishekh1123/job-listings-scraper.git
cd job-listings-scraper

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install requests beautifulsoup4
```

## Usage

```bash
python scraper.py
```

Output:

```
Scraped 100 jobs to jobs.csv
```

The scraper writes `jobs.csv` to the current directory, overwriting it on each run.

## Output Format

`jobs.csv` contains one header row and one row per listing:

| Column | Description |
| --- | --- |
| `title` | Job title |
| `company` | Company name |
| `location` | City and state |
| `url` | Link to the full job description page |

Sample rows:

```csv
title,company,location,url
Senior Python Developer,"Payne, Roberts and Davis","Stewartbury, AA",https://realpython.github.io/fake-jobs/jobs/senior-python-developer-0.html
Energy engineer,Vasquez-Davidson,"Christopherville, AA",https://realpython.github.io/fake-jobs/jobs/energy-engineer-1.html
```

Fields containing commas are quoted automatically by the `csv` module, so company names like `Payne, Roberts and Davis` survive a round trip intact.

## How It Works

The scraper follows a five-stage pipeline:

1. **Fetch** — `fetch_page()` requests the page and calls `raise_for_status()` so a bad response fails immediately rather than being parsed as HTML.
2. **Parse** — `parse_jobs()` builds a Beautiful Soup tree and narrows to the `#ResultsContainer` element.
3. **Find cards** — every listing is a `div.card` inside that container.
4. **Extract** — for each card, `.find()` is called *on the card itself*, not on the whole page. This scoping is what keeps a title bound to its own company and location.
5. **Write** — `save_to_csv()` uses `csv.DictWriter`, so column order comes from an explicit `FIELDNAMES` list rather than from dict insertion order.

### Page Structure

| Field | Selector |
| --- | --- |
| Job card | `div.card` |
| Title | `h2.title` |
| Company | `h3.company` |
| Location | `p.location` |
| Apply link | `a` with the text `Apply` |

The Apply link is matched by its text rather than by position among the two footer links, so the scraper does not silently break if the link order changes.

## Edge Case Handling

| Case | Behavior |
| --- | --- |
| HTTP error (4xx / 5xx) | `raise_for_status()` raises, halting before parsing |
| Results container missing | Returns an empty list instead of raising `AttributeError` |
| A field element is missing | Helper returns `""`; the remaining fields still save |
| An `<a>` has no `href` | `.get()` returns the default instead of raising `KeyError` |
| Commas or quotes in a field | Escaped by the `csv` module |
| Non-ASCII characters | File opened with `encoding="utf-8"` |

`find()` returns `None` rather than raising when nothing matches, so every lookup goes through a helper that checks for `None` first. Without that, one listing missing a location would kill the entire run and leave no output file.

## Project Structure

```
job-listings-scraper/
├── scraper.py      # The scraper
├── README.md
├── .gitignore
└── jobs.csv        # Generated output (not committed)
```

## Design Notes

- **Fetching and parsing are separate functions.** `parse_jobs()` takes an HTML string, not a URL, so parsing logic can be tested against a saved page without repeatedly hitting the live site.
- **Each job is a dict, not a tuple.** Keys double as CSV column headers and make the extraction code readable.
- **`if __name__ == "__main__":`** guards `main()`, so importing the module does not trigger a network request as a side effect.

## Possible Improvements

- Filter listings by keyword or location from the command line
- Follow each Apply link to scrape the full job description
- Handle pagination for sites that split results across pages
- Add a `--output` flag to set the CSV path
- Write to JSON as an alternative format
- Add retry logic with backoff for transient network failures
