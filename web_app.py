import write2db as db
import pandas as pd
import streamlit as st
import plotly.express as px
import yfinance as yf

# Data from DB
query = 'SELECT id, source, headline, sentiment, sentiment_score, scraped FROM headlines;'
df = db.read_db(query)

# Stock market data
sp500 = yf.Ticker("^GSPC")
sp500_hist = sp500.history(period="1mo").reset_index()

# Sidebar menu
# st.sidebar.title("📌 Menu")
# menu = st.sidebar.radio(
#     "Navigate to:",
#     ["Sentiment Distribution", "Latest Headlines"]
# )

# ------------------Streamlit layout------------------
st.title("📈 Financial News Sentiment")

# Sentiment Distribution
st.subheader("Sentiment Distribution")
sentiment_counts = df['sentiment'].value_counts().reset_index()
sentiment_counts.columns = ["sentiment", "count"]

fig = px.pie(sentiment_counts, values="count", names="sentiment", 
             color="sentiment", title="Overall Sentiment")
st.plotly_chart(fig)

# Average sentiment over days
daily_sentiment = df.groupby(df['scraped'].dt.date)['sentiment_score'].mean().reset_index()
daily_sentiment.columns = ['date', 'avg_sentiment_score']

fig = px.line(daily_sentiment, x='date', y='avg_sentiment_score', title='Average Sentiment Over Time', markers=True)
st.plotly_chart(fig)

# S&P 500
fig = px.line(sp500_hist, x="Date", y="Close", title="S&P500 Closing Price (Last 1 Month)", markers=True)
st.plotly_chart(fig)

# Latest Headlines
st.subheader("Latest Headlines")
st.dataframe(df[['scraped', 'source', 'headline', 'sentiment', 'sentiment_score']].sort_values("scraped", ascending=False))