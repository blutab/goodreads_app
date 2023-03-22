import streamlit as st
import pandas as pd
import numpy as np
import xmltodict
from utils import get_user_data
from collections import Counter
import seaborn as sns
from matplotlib.figure import Figure

st.set_page_config(layout="wide")
st.title('Analysis of your reading habits using Goodreads Data')


user_input = st.text_input("Enter your Goodreads profile URL (eg. https://www.goodreads.com/user/show/55130422-batul-bombaywala): ",
                           '55130422-batul-bombaywala')

user_input = user_input.split('/')[-1]

user_id = "".join(filter(lambda i: i.isdigit(), user_input))
user_name = user_input.split(user_id, 1)[1].split("-", 1)[1].replace("-", " ")

st.header("Analyzing the Reading History of: **{}**".format(user_name.title()))

user_input = str(user_input)
contents = get_user_data(user_id=user_id, v="2", shelf="read", per_page="200")

contents = xmltodict.parse(contents)
############################################
df = pd.DataFrame.from_dict(contents['GoodreadsResponse']['reviews']['review'])
df['rating'] = df['rating'].astype(float)

book_data = pd.json_normalize(df['book'])
book_data['average_rating'] = book_data['average_rating'].astype(float)
book_data['published'] = book_data['published'].fillna('0')
book_data['published'] =book_data['published'].astype(float)
book_data['num_pages'] = book_data['num_pages'].fillna('0')
book_data['num_pages'] =book_data['num_pages'].astype(float)

c = Counter(book_data['authors.author.name'])


year_read = Counter(sorted([int(item.split()[-1]) for item in df['read_at'] if item]))
books_published = book_data[['title','published']]
books_published = books_published.loc[books_published.published != 0]
books_published = books_published.sort_values(by = ['published'])
rating_df = pd.concat([book_data['title'],df['rating'],book_data['average_rating']],axis=1)
rating_df = rating_df.loc[rating_df.rating > 0]
rating_df['rating_diff'] = rating_df['rating'] - rating_df['average_rating']
rating_diff = round(abs(rating_df['rating_diff'].mean()),2)
rating_df['rating_diff'] = rating_df['rating_diff'].apply(abs)
rating_df = rating_df.sort_values(by = ['rating_diff'])

merged = pd.merge(rating_df, book_data[['title', 'num_pages', 'authors.author.name']], on='title' )



col1, col2 = st.columns(2)

with col1:
    st.header('Books read per year')
    fig = Figure()
    ax = fig.subplots()
    sns.barplot(x=list(year_read.keys()), y=list(year_read.values()), ax = ax)
    ax.set_xlabel("Year")
    ax.set_ylabel("Books Read")
    st.pyplot(fig)
    st.markdown(f"""You read a total of **{len(df)}** books from **{len(c)}** 
                different authors. You 
                read the most number of books from **{max(c, key=c.get)}**""")


    st.header('Your rating count')
    rating = Counter(sorted([item for item in df['rating'] if item > 0]))
    fig = Figure()
    ax = fig.subplots()
    sns.barplot(x=list(rating.keys()), y=list(rating.values()), ax= ax)
    ax.set_xlabel("Your Rating")
    ax.set_ylabel("Count")
    st.pyplot(fig)


    st.header('Distribution of number of pages for books you read')
    fig = Figure()
    ax = fig.subplots()
    sns.histplot(book_data['num_pages'], kde=True, ax = ax)
    ax.set_xlabel("Number of pages")
    ax.set_ylabel("Count")
    st.pyplot(fig)

    st.header('Your worst books according to average user')
    st.dataframe(rating_df.sort_values('average_rating')[:5][['title','average_rating']])

    st.header('Comparison of your rating with other users')
    fig = Figure()
    ax = fig.subplots()
    sns.scatterplot(x=rating_df['average_rating'], y=rating_df['rating'], ax=ax)
    ax.set_xlabel("Average Rating")
    ax.set_ylabel("Your rating")
    st.pyplot(fig)
    st.markdown(
        f"""Your rating differs from an average user by **{rating_diff}** points and 
        the book with the most difference is **{rating_df.iloc[-1]['title']}** where you rated 
        '**{rating_df.iloc[-1]['rating']}** stars and the average rating was **{rating_df.iloc[-1]['average_rating']}** stars"""
    )

with col2:
    st.header('When were your books published')
    fig = Figure()
    ax = fig.subplots()
    sns.histplot(books_published['published'], kde = True, ax = ax)
    ax.set_xlabel("Year")
    ax.set_ylabel("Number of Books published")
    st.pyplot(fig)
    st.markdown(
        f"""The oldest published book you read is **{books_published.iloc[0]['title']}** and the youngest
        published book you read is **{books_published.iloc[-1]['title']}**""")

    st.header('How others rated your books')
    fig = Figure()
    ax = fig.subplots()
    sns.histplot(book_data['average_rating'], kde=True, ax = ax)
    ax.set_xlabel("Average Rating")
    ax.set_ylabel("Number of Books")
    st.pyplot(fig)

    st.header('Correlation between your rating and number of pages')
    fig = Figure()
    ax = fig.subplots()
    sns.scatterplot(x=merged['rating'], y=merged['num_pages'], ax=ax)
    ax.set_xlabel("Your Rating")
    ax.set_ylabel("Number of pages")
    st.pyplot(fig)


    st.header('Your best books according to average user')
    st.dataframe(rating_df.sort_values('average_rating',ascending=False)[:5][['title','average_rating']])

