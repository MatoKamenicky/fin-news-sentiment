import write2db as db
import pandas as pd
import streamlit as st
import plotly.express as px
import yfinance as yf
import plotly.graph_objects as go

# Data from DB
query = 'SELECT id, source, headline, sentiment, sentiment_score, scraped FROM headlines_market_hours;'
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
market_sentiment = six_hour_sentiment[
    (six_hour_sentiment['Datetime_6h'].dt.hour >= 9) &
    (six_hour_sentiment['Datetime_6h'].dt.hour < 16)
]

# Merge with S&P 500 data
sp500_6h['Datetime_6h'] = sp500_6h['Datetime_6h'].dt.tz_convert(None)
# merged = pd.merge(six_hour_sentiment, sp500_6h, on='Datetime_6h', how='outer').sort_values('Datetime_6h')


# ------------------Streamlit layout---------------------------------------------
st.markdown("""
    <style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 1200px;
        margin: auto;
    }
    </style>
""", unsafe_allow_html=True)


# Page title and subtitle
st.title("📈 Financial News Sentiment")
st.subheader("Realtime sentiment, market trends, and actionable insights")

# --------------------------------------------------------------------------------

# --------------------------------------------------------------------------------

# Calculate metrics
latest_sp500 = sp500_hist['Close'].iloc[-1]
avg_sentiment_24h = six_hour_sentiment['avg_sentiment_score'].tail(4).mean() 
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

# AI Insights
st.header("AI Insights")


# --- 3. Correlation with S&P500 ---
if six_hour_sentiment['avg_sentiment_score'].notna().sum() > 5 and sp500_hist['Close'].notna().sum() > 5:
    corr = six_hour_sentiment['avg_sentiment_score'].corr(sp500_hist['Close'])
    st.info(f"📊 Correlation between sentiment & S&P500 (last {len(sp500_hist)} bins): {corr:.2f}")

# --------------------------------------------------------------------------------

# Sentiment Distribution
sentiment_counts = df['sentiment'].value_counts().reset_index()
sentiment_counts.columns = ["sentiment", "count"]

fig = px.pie(sentiment_counts, values="count", names="sentiment", 
             color="sentiment", title="Overall Sentiment")
st.plotly_chart(fig)

# --------------------------------------------------------------------------------

# Plot scraped data
fig = px.line(market_sentiment, x='Datetime_6h', y='avg_sentiment_score', title='Average Sentiment (6-hour intervals)', markers=True)
st.plotly_chart(fig)

# Plot S&P 500
fig = px.line(sp500_hist, x="Datetime", y="Close", title="S&P500 Closing Price (Last 1 day)", markers=True)
st.plotly_chart(fig)

# --------------------------------------------------------------------------------

# Latest Headlines
st.subheader("Latest Headlines")
st.dataframe(df[['scraped', 'source', 'headline', 'sentiment', 'sentiment_score']].sort_values("scraped", ascending=False))