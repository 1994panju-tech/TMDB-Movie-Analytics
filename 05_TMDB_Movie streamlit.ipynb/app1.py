import streamlit as st 
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import seaborn as sns
import sqlalchemy
from sqlalchemy import create_engine
engine = create_engine(
    "mysql+pymysql://root:root@localhost/movies")
import pymysql

conn=pymysql.connect(
    host="localhost",
    user="root",
    password="root",
    database="movies")

#headline

st.set_page_config(page_title="Movie SQL Analytics",layout="wide")
st.title("🎬 Movie SQL Query to Chart Dashboard")




# 1. Setup In-Memory Database (or connect to your real SQL database)
@st.cache_resource
def setup_database():
    conn = sqlite3.connect(':memory:', check_same_thread=False)
# Load CSVs as SQL tables
    pd.read_csv('movies_cleaned.csv').to_sql('movies_cleaned', conn, index=False)
    pd.read_csv('genres_cleaned.csv').to_sql('genres_cleaned', conn, index=False)
    pd.read_csv('movie_genres_cleaned.csv').to_sql('movie_genres_cleaned', conn, index=False)
    pd.read_csv('cast_cleaned.csv').to_sql('cast_cleaned', conn, index=False)
    pd.read_csv('crew_cleaned.csv').to_sql('crew_cleaned', conn, index=False)
    pd.read_csv('movie_keywords_cleaned.csv').to_sql('movie_keywords_cleaned', conn, index=False)
    return conn

conn = setup_database()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("📊 Visualization")

choice = st.sidebar.selectbox(
    "Select Analysis",
    [
        "1. Average Rating by Genre",
        "2. Revenue vs Budget",
        "3. Top 10 Grossing Movies",
        "4. Top 10 Movies by Budget",
        "5. Popularity vs Vote Count",
        "6. Number of Movies by Genre",
        "7. Average Revenue by Genre",
        "8. Average Budget by Genre",
        "9. Top 10 Actors by Movie Count",
        "10. Top 10 Movies by Profit"
    ]
)


# ============================================================
# 1. AVERAGE RATING BY GENRE
# ============================================================

if choice == "1. Average Rating by Genre":

    st.subheader("⭐ Average Movie Rating by Genre")

    query = """
    SELECT
        g.genre_name,
        AVG(m.vote_average) AS avg_rating
    FROM movie_genres_cleaned mg
    JOIN genres_cleaned g
        ON mg.genre_id = g.genre_id
    JOIN movies_cleaned m
        ON mg.movie_id = m.movie_id
    GROUP BY g.genre_name
    ORDER BY avg_rating DESC;
    """

    df = pd.read_sql(query, conn)

    fig, ax = plt.subplots(figsize=(10, 5))

    sns.barplot(data=df,x="genre_name",y="avg_rating",ax=ax)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Rating")
    ax.set_ylim(0, 10)

    plt.xticks(rotation=45,ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)


# ============================================================
# 2. REVENUE VS BUDGET
# ============================================================

elif choice == "2. Revenue vs Budget":

    st.subheader("💰 Revenue vs Budget")

    query = """
    SELECT
        title,
        budget,
        revenue
    FROM movies_cleaned
    WHERE budget > 0
      AND revenue > 0;
    """

    df = pd.read_sql(query, conn)

    # Convert to millions
    df["budget"] = df["budget"] / 1000000
    df["revenue"] = df["revenue"] / 1000000

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.scatterplot(data=df,x="budget",y="revenue",ax=ax)

    ax.set_xlabel("Budget ($ Millions)")
    ax.set_ylabel("Revenue ($ Millions)")
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)


# ============================================================
# 3. TOP 10 GROSSING MOVIES
# ============================================================

elif choice == "3. Top 10 Grossing Movies":

    st.subheader("🏆 Top 10 Highest-Grossing Movies")

    query = """
    SELECT
        title,
        revenue
    FROM movies_cleaned
    WHERE revenue > 0
    ORDER BY revenue DESC
    LIMIT 10;
    """

    df = pd.read_sql(query, conn)
    df["revenue"] = df["revenue"] / 1000000000
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(data=df,y="title",x="revenue",ax=ax )
    ax.set_xlabel("Revenue ($ Billions)")
    ax.set_ylabel("Movie")
    plt.tight_layout()
    st.pyplot(fig)

    st.dataframe(df, use_container_width=True)


# ============================================================
# 4. TOP 10 MOVIES BY BUDGET
# ============================================================

elif choice == "4. Top 10 Movies by Budget":

    st.subheader("💵 Top 10 Movies by Budget")

    query = """
    SELECT
        title,
        budget
    FROM movies_cleaned
    WHERE budget > 0
    ORDER BY budget DESC
    LIMIT 10;
    """

    df = pd.read_sql(query, conn)

    df["budget"] = df["budget"] / 1000000
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(data=df,y="title",x="budget",ax=ax)
    ax.set_xlabel("Budget ($ Millions)")
    ax.set_ylabel("Movie")
    plt.tight_layout()
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)


# ============================================================
# 5. POPULARITY VS VOTE COUNT
# ============================================================

elif choice == "5. Popularity vs Vote Count":

    st.subheader("📈 Popularity vs Vote Count")

    query = """
    SELECT
        title,
        popularity,
        vote_count
    FROM movies_cleaned
    WHERE popularity IS NOT NULL
      AND vote_count IS NOT NULL;
    """

    df = pd.read_sql(query, conn)
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.scatterplot( data=df,x="popularity",y="vote_count",ax=ax)
    ax.set_xlabel("Popularity")
    ax.set_ylabel("Vote Count")
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)


# ============================================================
# 6. NUMBER OF MOVIES BY GENRE
# ============================================================

elif choice == "6. Number of Movies by Genre":

    st.subheader("🎭 Number of Movies by Genre")

    query = """
    SELECT
        g.genre_name,
        COUNT(DISTINCT mg.movie_id) AS movie_count
    FROM movie_genres_cleaned mg
    JOIN genres_cleaned g
        ON mg.genre_id = g.genre_id
    GROUP BY g.genre_name
    ORDER BY movie_count DESC;
    """

    df = pd.read_sql(query, conn)
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(data=df,x="genre_name",y="movie_count",ax=ax)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Number of Movies")

    plt.xticks(rotation=45,ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)


# ============================================================
# 7. AVERAGE REVENUE BY GENRE
# ============================================================

elif choice == "7. Average Revenue by Genre":

    st.subheader("💰 Average Revenue by Genre")

    query = """
    SELECT
        g.genre_name,
        AVG(m.revenue) AS avg_revenue
    FROM movie_genres_cleaned mg
    JOIN genres_cleaned g
        ON mg.genre_id = g.genre_id
    JOIN movies_cleaned m
        ON mg.movie_id = m.movie_id
    WHERE m.revenue > 0
    GROUP BY g.genre_name
    ORDER BY avg_revenue DESC;
    """

    df = pd.read_sql(query, conn)
    df["avg_revenue"] = df["avg_revenue"] / 1000000
    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(data=df,x="genre_name",y="avg_revenue",ax=ax)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Revenue ($ Millions)")
    plt.xticks(rotation=45,ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)


# ============================================================
# 8. AVERAGE BUDGET BY GENRE
# ============================================================

elif choice == "8. Average Budget by Genre":

    st.subheader("💵 Average Budget by Genre")

    query = """
    SELECT
        g.genre_name,
        AVG(m.budget) AS avg_budget
    FROM movie_genres_cleaned mg
    JOIN genres_cleaned g
        ON mg.genre_id = g.genre_id
    JOIN movies_cleaned m
        ON mg.movie_id = m.movie_id
    WHERE m.budget > 0
    GROUP BY g.genre_name
    ORDER BY avg_budget DESC;
    """

    df = pd.read_sql(query, conn)
    df["avg_budget"] = df["avg_budget"] / 1000000
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df,x="genre_name",y="avg_budget",ax=ax)
    ax.set_xlabel("Genre")
    ax.set_ylabel("Average Budget ($ Millions)")
    plt.xticks(rotation=45,ha="right")
    plt.tight_layout()
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)


# ============================================================
# 9. TOP 10 ACTORS BY MOVIE COUNT
# ============================================================

elif choice == "9. Top 10 Actors by Movie Count":

    st.subheader("🎭 Top 10 Actors by Movie Count")

    query = """
    SELECT
        actor_name,
        COUNT(DISTINCT movie_id) AS movie_count
    FROM cast_cleaned
    GROUP BY actor_name
    ORDER BY movie_count DESC
    LIMIT 10;
    """

    df = pd.read_sql(query, conn)

    fig, ax = plt.subplots(figsize=(10, 6))

    sns.barplot(data=df,y="actor_name",x="movie_count",ax=ax)
    ax.set_xlabel("Number of Movies")
    ax.set_ylabel("Actor")
    plt.tight_layout()
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)


# ============================================================
# 10. TOP 10 MOVIES BY PROFIT
# ============================================================

elif choice == "10. Top 10 Movies by Profit":

    st.subheader("🏆 Top 10 Movies by Profit")

    query = """
    SELECT
        title,
        budget,
        revenue,
        revenue - budget AS profit
    FROM movies_cleaned
    WHERE budget > 0
      AND revenue > 0
    ORDER BY profit DESC
    LIMIT 10;
    """

    df = pd.read_sql(query, conn)

    df["profit"] = df["profit"] / 1000000000
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=df,y="title",x="profit",ax=ax)
    ax.set_xlabel("Profit ($ Billions)")
    ax.set_ylabel("Movie")
    plt.tight_layout()
    st.pyplot(fig)
    st.dataframe(df, use_container_width=True)

    conn.commit()