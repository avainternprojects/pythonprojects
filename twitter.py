import streamlit as st
import pandas as pd
from nltk.sentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import matplotlib.pyplot as plt 
st.title("Twitter Airlinr sentiment")
st.warning("first download the dataset from kaggle")
upload_file=st.file_uploader("Upload twitter.py" ,type="csv")

if upload_file:
    df=pd.read_csv(upload_file)

    airline=st.selectbox("select Airline",df['airline'].unique())
    airline_df=df[df['airline']==airline]

    sia = SentimentIntensityAnalyzer()
    airline_df['sentiment']=airline_df['text'].apply(lambda x:sia.polarity_scores(x)['compound'])

    col1,col2=st.columns(2)
    with col1:
        st.subheader("Sentiment Distribution")
        st.bar_chart(airline_df['sentiment'].value_counts())

    with col2:
        st.subheader("Word Cloud")
        text="".join(tweet for tweet in airline_df['text'])
        wordcloud=WordCloud().generate(text)
        plt.imshow(wordcloud,interpolation='bilinear')
        plt.axis("off")
        st.pyplot(plt)

        st.subheader("Sample tweets")
        sentiment_filter=st.radio("Filter by:",['ALL','Positive','Neutral','Negative'])
        sample_tweets=airline_df[airline_df['sentiment']==sentiment_filter] if sentiment_filter !='All' else airline_df
        st.table(sample_tweets[['text','sentiment']].head(5))