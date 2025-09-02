# Financial News Sentiment Analysis

A **Python** project for scraping financial news, performing sentiment analysis, storing results in a database, and visualizing insights via a web app.  
This tool is designed to help you gain deeper insights into the financial world and make more informed investing and financial decisions.

---

## Features

- **scraper.py** — Fetches news articles from financial websites for analysis.  
- **analysis.py** — Runs sentiment analysis on scraped news data.  
- **write2db.py** — Connects to the database and writes sentiment results.  
- **web_app.py** — Streamlit-powered web application for interactive sentiment visualization.  

---

## Prerequisites

- Python 3.8+  
- Ussed packages:  
  - `pandas`  
  - `beautifulsoup4`  
  - `nltk`
  - `asyncio`
  - `aiohttp`
  - `plotly`
  - `yfinance `
  - `streamlit`
  - `psycopg2`

---

## Future Enhancements

- Add support for more financial news sources (currently only 3).  
- Automate news scraping to refresh data every few hours.  
- Implement advanced NLP techniques (e.g., transformers, entity-level sentiment).  
- Real-time sentiment dashboards with live feeds.  
- Dockerize the app for seamless deployment.  
- Add CI/CD pipelines (e.g., GitHub Actions) for automated testing & deployment.  
