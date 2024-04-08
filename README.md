# News Scraper

## Overview
This Python script scrapes news articles from various search engines such as Google, Yahoo, and Bing based on the provided company names and keywords. It saves the scraped data into a CSV file.

## Features
- Scrapes news articles from Google, Yahoo, and Bing.
- Supports multiprocessing for faster scraping.
- Converts the timeframe format of scraped articles.
- Logs errors and completion messages.

## Installation
1. Clone the repository:
```bash
git clone https://github.com/siddhijagtap7/scraping_multiprocessing.git
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage
1. Fill in the `config.json` file with the desired search companies, keywords, and number of pages to scrape.
2. Run the script:
```bash
python scrape.py
```
