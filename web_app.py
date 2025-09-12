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



df['scraped_time_rounded'] = df['scraped'].dt.floor('10min')
market_sentiment = df.groupby('scraped_time_rounded')['sentiment_score'].mean().reset_index()
market_sentiment.columns = ['scraped_time', 'avg_sentiment_score']

# ------------------Streamlit layout---------------------------------------------
st.set_page_config(page_title="Financial News Sentiment", layout="wide")

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

st.markdown( """
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       """, unsafe_allow_html=True)

st.markdown("""
    <style>
    /* Card padding & color */
    .stMetric {
        background-color: #1E1E1E;
        border-radius: 10px;
        padding: 10px;
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
avg_sentiment_24h = market_sentiment['avg_sentiment_score'].tail(4).mean() 
headlines_today = df[df['scraped'].dt.date == pd.Timestamp.today().date()].shape[0]
sentiment_volatility = market_sentiment['avg_sentiment_score'].tail(4).std()

if len(market_sentiment) >= 5:
    sentiment_trend = (market_sentiment['avg_sentiment_score'].iloc[-1] - market_sentiment['avg_sentiment_score'].iloc[-5]) / abs(market_sentiment['avg_sentiment_score'].iloc[-5]) * 100
else:
    sentiment_trend = None


# Display summary cards
st.header("Summary")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest S&P500 Close", f"{latest_sp500:.2f}")
col2.metric("Average Sentiment (24h)", f"{avg_sentiment_24h:.2f}")
col3.metric("Headlines Today", headlines_today)


trend_display = f"{sentiment_trend:.1f}%" if sentiment_trend is not None else "N/A"
volatility_display = f"{sentiment_volatility:.2f}" if sentiment_volatility is not None else "N/A"

col4.metric("Sentiment Volatility", volatility_display, delta=trend_display)
# col4.metric("Sentiment Volatility", f"{sentiment_volatility:.2f}", delta=f"{sentiment_trend:.1f}%")

# --------------------------------------------------------------------------------

# AI Insights
st.header("AI Insights")


# --- 3. Correlation with S&P500 ---
if market_sentiment['avg_sentiment_score'].notna().sum() > 5 and sp500_hist['Close'].notna().sum() > 5:
    corr = market_sentiment['avg_sentiment_score'].corr(sp500_hist['Close'])
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
fig = px.line(market_sentiment, x='scraped_time', y='avg_sentiment_score', title='Average Sentiment', markers=True)
st.plotly_chart(fig)

# Plot S&P 500
fig = px.line(sp500_hist, x="Datetime", y="Close", title="S&P500 Closing Price (Last 1 day)", markers=True)
st.plotly_chart(fig)

# --------------------------------------------------------------------------------

# Latest Headlines
st.subheader("Latest Headlines")
st.dataframe(df[['scraped', 'source', 'headline', 'sentiment', 'sentiment_score']].sort_values("scraped", ascending=False))