import psycopg2
from datetime import datetime
import re
import pandas as pd

def db_conn():
    conn = psycopg2.connect(
                user="postgres",
                password="postgres",
                host="localhost",
                port="5432",
                dbname="newsdb"
                )
    return conn

def read_db(query):
    conn = db_conn()
    df = pd.read_sql(query, conn)

    return df

def sentiment2db(df):
    conn = db_conn()
    cursor = conn.cursor()

    for index, row in df.iterrows():
        update_query = """
            UPDATE headlines
            SET sentiment_score=%s, sentiment=%s
            WHERE id = %s;
        """
        cursor.execute(update_query, (row['sentiment_score'], row['sentiment'], row['id']))

    conn.commit()

    cursor.close()
    conn.close()
    print("PostgreSQL connection is closed")


def headlines2db(url,headlines):
    conn = None
    try:
        conn = db_conn()
        
        conn.autocommit = True
        cursor = conn.cursor()

        pattern = re.compile(r"https?://(?:www\.|edition\.)?([a-zA-Z0-9-]+)\.")

        match = pattern.search(url)
        if match:
            source = match.group(1)
        else:
            source = None

        for h in headlines:
            query = """
                    INSERT INTO headlines(source, headline, url, scraped)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (source, headline) DO NOTHING;
                    """
            cursor.execute(query, (source, h, url, datetime.now()))
       
        count = cursor.rowcount
        print(count, "Record inserted successfully into table")

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into table", error)

    finally:
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")