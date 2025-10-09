# Financial News Sentiment Analysis

A **Python project** for scraping financial news, performing sentiment analysis, storing results in a Supabase database, and visualizing insights through a web app.  

**[👉 Try the Live Streamlit App](https://finpulseapp.streamlit.app)**  

## 📘 Overview
The system automatically collects fresh financial news at 7:30, 9:30, 12:00, 15:30, 18:00, analyzes the sentiment of each article, and stores the results in a structured database. Visualization tools then provide clear insights into market trends, helping users make more informed investment and financial decisions. The Streamlit web app also offers AI-powered insights using the Hugging Face API, sentiment comparison with selected stocks, and much more.  

Automated scraping and scheduled updates are powered by **GitHub Actions**, ensuring the pipeline runs seamlessly without manual intervention.

---

## ⚙️ Features

- **scraper.py** — Fetches news articles from financial websites for analysis.  
- **analysis.py** — Runs sentiment analysis on scraped news data.  
- **write2db.py** — Connects to the database and writes sentiment results.  
- **web_app.py** — Streamlit-powered web application for interactive sentiment visualization.
- **main.py** — Main file for running scrapper and analysis automaticly using github actions. 

---

## 🚀 Future Enhancements
  
- Implement advanced NLP techniques (e.g., transformers, entity-level sentiment).  
- Real-time sentiment dashboards with live feeds.  
- Dockerize the app for seamless deployment.  
- Add CI/CD pipelines (e.g., GitHub Actions) for automated testing & deployment.  
