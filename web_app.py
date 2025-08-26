import write2db as db
import pandas as pd
import streamlit as st
import plotly.express as px

query = 'SELECT id, source, headline, sentiment, sentiment_score, scraped FROM headlines;'
df = db.read_db(query)

# Streamlit layout
st.title("📈 Financial News Sentiment Dashboard")

st.subheader("Sentiment Distribution")
sentiment_counts = df['sentiment'].value_counts().reset_index()
sentiment_counts.columns = ["sentiment", "count"]

fig = px.pie(sentiment_counts, values="count", names="sentiment", 
             color="sentiment", title="Overall Sentiment")
st.plotly_chart(fig)

st.subheader("Latest Headlines")
st.dataframe(df[['scraped', 'source', 'headline', 'sentiment', 'sentiment_score']].sort_values("scraped", ascending=False))