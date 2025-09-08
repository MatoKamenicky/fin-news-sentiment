import write2db as db
import pandas as pd
import streamlit as st
import plotly.express as px
import yfinance as yf
import plotly.graph_objects as go

# Data from DB
query = 'SELECT id, source, headline, sentiment, sentiment_score, scraped FROM headlines;'
df = db.read_db(query)

# Stock market data
sp500 = yf.Ticker("^GSPC")
sp500_hist = sp500.history(period="1d", interval="1h").reset_index()

# Floor to 6-hour intervals
sp500_hist['Datetime_6h'] = sp500_hist['Datetime'].dt.floor('6H')

sp500_6h = sp500_hist.groupby('Datetime_6h')['Close'].mean().reset_index()

# Average sentiment over 6-hour intervals
df['Datetime_6h'] = df['scraped'].dt.floor('6H')

# Group by 6-hour intervals
six_hour_sentiment = (df.groupby('Datetime_6h')['sentiment_score'].mean().reset_index())
six_hour_sentiment.columns = ['Datetime_6h', 'avg_sentiment_score']

# Merge with S&P 500 data
sp500_6h['Datetime_6h'] = sp500_6h['Datetime_6h'].dt.tz_convert(None)
# merged = pd.merge(six_hour_sentiment, sp500_6h, on='Datetime_6h', how='outer').sort_values('Datetime_6h')


# ------------------Streamlit layout---------------------------------------------
st.title("📈 Financial News Sentiment")
st.subheader("Realtime sentiment, market trends, and actionable insights")

# --------------------------------------------------------------------------------

# Calculate metrics
latest_sp500 = sp500_hist['Close'].iloc[-1]
avg_sentiment_24h = six_hour_sentiment['avg_sentiment_score'].tail(4).mean()  # last 24h = 4 x 6h bins
headlines_today = df[df['scraped'].dt.date == pd.Timestamp.today().date()].shape[0]
sentiment_volatility = six_hour_sentiment['avg_sentiment_score'].tail(4).std()
sentiment_trend = (six_hour_sentiment['avg_sentiment_score'].iloc[-1] - six_hour_sentiment['avg_sentiment_score'].iloc[-5]) / abs(six_hour_sentiment['avg_sentiment_score'].iloc[-5]) * 100

# Display summary cards
st.header("Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest S&P500 Close", f"{latest_sp500:.2f}")
col2.metric("Average Sentiment (24h)", f"{avg_sentiment_24h:.2f}")
col3.metric("Headlines Today", headlines_today)
col4.metric("Sentiment Volatility", f"{sentiment_volatility:.2f}", delta=f"{sentiment_trend:.1f}%")

# --------------------------------------------------------------------------------

# Sentiment Distribution
sentiment_counts = df['sentiment'].value_counts().reset_index()
sentiment_counts.columns = ["sentiment", "count"]

fig = px.pie(sentiment_counts, values="count", names="sentiment", 
             color="sentiment", title="Overall Sentiment")
st.plotly_chart(fig)

# --------------------------------------------------------------------------------

# Plot scraped data
fig = px.line(six_hour_sentiment, x='Datetime_6h', y='avg_sentiment_score', title='Average Sentiment (6-hour intervals)', markers=True)
st.plotly_chart(fig)

# Plot S&P 500
fig = px.line(sp500_hist, x="Datetime", y="Close", title="S&P500 Closing Price (Last 1 day)", markers=True)
st.plotly_chart(fig)

# --------------------------------------------------------------------------------

# Latest Headlines
st.subheader("Latest Headlines")
st.dataframe(df[['scraped', 'source', 'headline', 'sentiment', 'sentiment_score']].sort_values("scraped", ascending=False))