import os
from xmlrpc import client
from click import prompt
import write2db as db
import pandas as pd
import streamlit as st
import plotly.express as px
import yfinance as yf
import plotly.graph_objects as go
from huggingface_hub import InferenceClient

# ------------------Streamlit layout---------------------------------------------
    
st.set_page_config(page_title="Financial News Sentiment", layout="wide")

st.markdown("""
    <style>
    .space-grotesk-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: 2rem;
        color: white;
    }
    .space-grotesk-text {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 400;
        font-size: 1.05rem;
        color: #ccc;
    }
    .stMetric { 
        background: linear-gradient(145deg, #1E1E1E, #2A2A2A); 
        border-radius: 12px; 
        padding: 12px; 
        }
    </style>
""", unsafe_allow_html=True)


# Page title and subtitle
intro_html = """
<div style="background: linear-gradient(145deg, #0F0F0F, #161616);
            border-radius:12px; padding:16px; margin-bottom:18px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.6);">
  <h2 style="color:white; margin:0 0 6px 0;">Financial News Sentiment Dashboard</h2>
  <p style="color:#F0F0F0;; font-size:20px; margin:0 0 8px 0;">
    Combine news sentiment with market prices to spot correlations and potential market-moving headlines.
  </p>
  <div style="color:#BDBDBD; font-size:15px;">
    <strong>Quick tips:</strong>
    &nbsp;Use the sidebar to filter sources, sentiment, date range, and to select the stock/ETF to compare.
  </div>
</div>
"""
# st.markdown(intro_html, unsafe_allow_html=True)
st.markdown('<h2 class="space-grotesk-title">Financial News Sentiment Dashboard</h2>', unsafe_allow_html=True)
st.write('<p class="space-grotesk-text">Combine news sentiment with market prices to spot correlations and potential market-moving headlines.</p>', unsafe_allow_html=True)
st.write('<p class="space-grotesk-text"><strong>Quick tips:</strong> Use the sidebar to filter sources, sentiment, date range, and to select the stock/ETF to compare.</p>', unsafe_allow_html=True)
# --------------------------------------------------------------------------

# Data from DB
query = 'SELECT id, source, headline, sentiment, sentiment_score, scraped FROM headlines_market_hours;'
df = db.read_db(query)



df['scraped'] = pd.to_datetime(df['scraped'], errors='coerce')
df['scraped_time_rounded'] = df['scraped'].dt.floor('30min')
df['scraped_time_rounded'] = df['scraped_time_rounded'] - pd.Timedelta(hours=4)
df['scraped_time_rounded'] = df['scraped_time_rounded'].dt.tz_localize("America/New_York")

df_trend = df.copy()
# -------------------------------- Sidebar -------------------------------- 
st.sidebar.title('<p class="space-grotesk-text">Filters</p>', unsafe_allow_html=True)

# Source filter
sources = st.sidebar.multiselect(
    "Select News Sources",
    options=df["source"].unique(),
    default=df["source"].unique()
)

# Sentiment filter
sentiments = st.sidebar.multiselect(
    "Select Sentiments",
    options=df["sentiment"].unique(),
    default=df["sentiment"].unique()
)

# Date range filter
date_min, date_max = df["scraped_time_rounded"].min(), df["scraped_time_rounded"].max()
date_range = st.sidebar.date_input("Date Range", [date_max, date_max])

# Single or multiple days selection
if len(date_range) == 2:
    start_date = pd.to_datetime(date_range[0]).tz_localize("America/New_York")
    end_date   = pd.to_datetime(date_range[1]).tz_localize("America/New_York") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

elif  len(date_range) == 1:
    start_date = pd.to_datetime(date_range[0]).tz_localize("America/New_York")
    end_date   = pd.to_datetime(date_range[0]).tz_localize("America/New_York") + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)

# Ticker selection
@st.cache_data
def load_ticker_list():
    # Public dataset of NASDAQ-listed companies
    url = "https://raw.githubusercontent.com/datasets/nasdaq-listings/master/data/nasdaq-listed-symbols.csv"
    df = pd.read_csv(url)
    df = df.rename(columns={"Symbol": "Ticker", "Company Name": "Name"})
    return df[["Ticker", "Name"]]

# Load once and cache
ticker_df = load_ticker_list()

selected_name = st.sidebar.selectbox(
    "Select Stock / ETF to Compare",
    options=["-- Select a company --"] + ticker_df["Name"].tolist(),
    index=0
)

if selected_name == "-- Select a company --":
    selected_ticker = "^GSPC"  # Default to S&P 500 if none selected
else:
    selected_ticker = ticker_df.loc[ticker_df["Name"] == selected_name, "Ticker"].iloc[0]


# Load chosen ticker data
ticker = yf.Ticker(selected_ticker)
stock_hist = ticker.history(period="1mo", interval="1h").reset_index()


mask = (
    df["source"].isin(sources)
    & df["sentiment"].isin(sentiments)
    & (df["scraped_time_rounded"] >= start_date)
    & (df["scraped_time_rounded"] <= end_date)
)

stock_hist = stock_hist[
    (stock_hist["Datetime"] >= start_date) & 
    (stock_hist["Datetime"] <= end_date)
]

df_filtered = df[mask]
df = df_filtered.copy()

# --------------------------------------------------------------------------------------

# Aggregate sentiment scores over time
market_sentiment = df.groupby('scraped_time_rounded')['sentiment_score'].mean().reset_index()
market_sentiment.columns = ['scraped_time', 'avg_sentiment_score']
# --------------------------------------------------------------------------------------



# Calculate metrics
if not stock_hist.empty:
    latest_stock = stock_hist['Close'].iloc[-1]
else:
    latest_stock = float("nan")
headlines_today = df[df['scraped'].dt.date == pd.Timestamp.today().date()].shape[0]
sentiment_24h = market_sentiment.set_index("scraped_time").last("24H")
avg_sentiment_24h = sentiment_24h["avg_sentiment_score"].mean()
sentiment_volatility = sentiment_24h["avg_sentiment_score"].std()


# Sentiment trend over last 5 scrappings
if len(sentiment_24h) >= 5:
    sentiment_trend = (sentiment_24h['avg_sentiment_score'].iloc[-1] - sentiment_24h['avg_sentiment_score'].iloc[-5]) / abs(sentiment_24h['avg_sentiment_score'].iloc[-5])
else:
    sentiment_trend = None


# Display summary cards
st.markdown('<h2 class="space-grotesk-title">Summary</h2>', unsafe_allow_html=True)
col1, col2, col3, col4 = st.columns(4)
col1.metric("Latest Stock Close", f"{latest_stock:.2f}")
col2.metric("Average Sentiment (24h)", f"{avg_sentiment_24h:.2f}")
col3.metric("Headlines Today", headlines_today)


trend_display = f"{sentiment_trend:.1f}%" if sentiment_trend is not None else "N/A"
volatility_display = f"{sentiment_volatility:.2f}" if sentiment_volatility is not None else "N/A"

col4.metric("Sentiment Volatility", volatility_display, delta=trend_display)

merged = pd.merge_asof(
    stock_hist[["Datetime", "Close"]],
    market_sentiment,
    left_on="Datetime",
    right_on="scraped_time"
    )

# Calculate correlation
corr = merged["avg_sentiment_score"].corr(merged["Close"])

st.metric(f"Sentiment vs {selected_name} Close Correlation", f"{corr:.2f}")
# --------------------------------------------------------------------------------

# AI Insights
st.markdown('<h2 class="space-grotesk-title">AI Insight</h2>', unsafe_allow_html=True)



prompt = f"""
You are an AI financial assistant. Analyze the relationship between sentiment and {selected_ticker}.

- Average sentiment (24h): {avg_sentiment_24h:.2f}
- Correlation with {selected_ticker}: {corr:.2f}
- Recent headlines: {df_filtered['headline'].tolist()[:5]}
- Selected stock: {selected_name} ({selected_ticker})

Please generate a short, human-readable insight (2-3 sentences).
"""
HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(
    provider="novita",
    api_key=HF_API_KEY,
)

completion = client.chat.completions.create(
    model="meta-llama/Llama-3.2-3B-Instruct",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ],
)

response = completion.choices[0].message.content.strip()

st.markdown(response)
    
# --------------------------------------------------------------------------------

# Sentiment Distribution
sentiment_counts = df['sentiment'].value_counts().reset_index()
sentiment_counts.columns = ["sentiment", "count"]

fig_pie = px.pie(sentiment_counts, values="count", names="sentiment", 
             color="sentiment", title="Overall Sentiment")
# st.plotly_chart(fig)

# --------------------------------------------------------------------------------

# Plot scraped data
fig = px.line(market_sentiment, x='scraped_time', y='avg_sentiment_score', title='Average Sentiment', markers=True)
fig.update_traces(line=dict(color="#615FFF"))
st.plotly_chart(fig)

# Plot Selected Stock
fig = px.line(stock_hist, x="Datetime", y="Close", title=f"{selected_name} Closing Price", markers=True)
fig.update_traces(line=dict(color="#0077FF"))
st.plotly_chart(fig)

# --------------------------------------------------------------------------------


# Combined Sentiment and Selected Stock Plot
fig = go.Figure()
fig.add_trace(go.Scatter(x=market_sentiment["scraped_time"], y=market_sentiment["avg_sentiment_score"],
                         mode="lines+markers", name="Avg Sentiment", line=dict(color="#615FFF")))
fig.add_trace(go.Scatter(x=stock_hist["Datetime"], y=stock_hist["Close"],
                         mode="lines+markers", name=f"{selected_name} Close", yaxis="y2", line=dict(color="#0077FF")))

fig.update_layout(title=f"Sentiment vs {selected_name} Close", yaxis=dict(title="Sentiment Score"), yaxis2=dict(title=f"{selected_name} Close", overlaying="y", side="right"))
st.plotly_chart(fig, use_container_width=True)
# --------------------------------------------------------------------------------


sentiment_by_source = df_filtered.groupby("source")["sentiment_score"].mean().reset_index()
fig_source = px.bar(
    sentiment_by_source, x="source", y="sentiment_score",
    title="Average Sentiment by Source",
    color="sentiment_score", color_continuous_scale="RdYlGn"
)

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(fig_pie, use_container_width=True) 
with col2:
    st.plotly_chart(fig_source, use_container_width=True)

# Latest Headlines
st.subheader("Latest Headlines")
st.dataframe(
    df_filtered[['scraped', 'source', 'headline', 'sentiment', 'sentiment_score']]
    .sort_values("scraped", ascending=False)
    .style.applymap(lambda v: "color: green;" if v=="positive" else "color: red;" if v=="negative" else "color: gray;", subset=["sentiment"])
)