# Financial News Sentiment Analysis

A **Python project** for scraping financial news, performing sentiment analysis, storing results in a Supabase database, and visualizing insights through a web app.  

The system automatically collects fresh financial news every **6 hours**, analyzes the sentiment of each article, and stores the results in a structured database. Visualization tools then provide clear insights into market trends, helping users make more informed investment and financial decisions.  

Automated scraping and scheduled updates are powered by **GitHub Actions**, ensuring the pipeline runs seamlessly without manual intervention.


---

## Features

- **scraper.py** — Fetches news articles from financial websites for analysis.  
- **analysis.py** — Runs sentiment analysis on scraped news data.  
- **write2db.py** — Connects to the database and writes sentiment results.  
- **web_app.py** — Streamlit-powered web application for interactive sentiment visualization.
- **main.py** — Main file for running scrapper and analysis automaticly using github actions. 


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
- Implement advanced NLP techniques (e.g., transformers, entity-level sentiment).  
- Real-time sentiment dashboards with live feeds.  
- Dockerize the app for seamless deployment.  
- Add CI/CD pipelines (e.g., GitHub Actions) for automated testing & deployment.  
