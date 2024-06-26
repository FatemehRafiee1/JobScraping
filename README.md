# Job Scraping and Keyword Extraction

This Python script is designed to scrape job listings from LinkedIn, extract relevant details such as job title, company, date published, location, and URL link, and perform keyword extraction from job descriptions by using Named Entity Recognition (NER). The extracted data is then stored in a CSV file for further analysis.

## Setup

### Prerequisites
- Python 3.x installed
- Required Python packages installed (you can install them via pip):
  - `requests`
  - `pandas`
  - `beautifulsoup4`

### Installation
1. Clone or download the repository containing the script.
2. Make sure you have the necessary files:
   - `key_extractor.py` (for keyword extraction)
   - `proxy.txt` (contains a list of proxies from [this site](https://advanced.name/freeproxy))
   - `user_agents.txt` (contains a list of user agents created randomly)
3. Customize the script as needed (e.g., adjust URLs, file paths, or scraping parameters).

## Usage
1. Run the script `job_scraper.py`.
2. The script will scrape job listings from LinkedIn based on predefined search parameters (e.g., job title, location).
3. Extracted job details and keywords will be stored in a CSV file specified in the script.

## File Structure
- `job_scraper.py`: Main Python script for job scraping and analysis.
- `key_extractor.py`: Module for keyword extraction from job descriptions.
- `proxy.txt`: Text file containing a list of proxies for handling requests.
- `user_agents.txt`: Text file containing a list of user agents for request headers.
- `README.md`: This file, providing an overview of the project.

## Notes
- Ensure that you have a reliable internet connection as the script relies on web scraping.
- Make sure to comply with LinkedIn's terms of service and usage limits to avoid being blocked. Basically don't send too many request in a short period of time. 