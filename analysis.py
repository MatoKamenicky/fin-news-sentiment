import write2db as db
import pandas as pd
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# DB connection
query = 'SELECT id, source, headline, scraped FROM headlines WHERE sentiment IS NULL;'

df = db.read_db(query)

# Sentiment analysis calculation
def sentiment_analysis(df):
    nltk.download("vader_lexicon")

    sia = SentimentIntensityAnalyzer()

    df['sentiment_score'] = df['headline'].apply(lambda x: sia.polarity_scores(x)['compound'])
    df['sentiment'] = df['sentiment_score'].apply(lambda score: 'positive' if score >= 0.05 else ('negative' if score < -0.05 else 'neutral'))

    print("Sentiment analysis completed.")
    return df

df = sentiment_analysis(df)

# Update sentiment in database
db.sentiment2db(df)