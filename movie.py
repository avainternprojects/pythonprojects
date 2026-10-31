import streamlit as st
import nltk
from nltk.corpus import movie_reviews
from nltk.sentiment import SentimentIntensityAnalyzer
import random

# Initialize
nltk.download(['movie_reviews', 'vader_lexicon'])
sia = SentimentIntensityAnalyzer()

# App UI
st.title("🎬 Movie Review Sentiment")
st.write("Analyzing NLTK's movie reviews corpus")

# Load data
reviews = [(movie_reviews.raw(fileid), category) 
          for category in movie_reviews.categories() 
          for fileid in movie_reviews.fileids(category)]
random.shuffle(reviews)

# Interactive analysis
review_sample = st.selectbox("Choose a review sample:", 
                           [f"{x[0][:50]}... ({x[1]})" for x in reviews[:20]])

if st.button("Analyze Sentiment"):
    full_text = next(x[0] for x in reviews if review_sample.startswith(x[0][:50]))
    scores = sia.polarity_scores(full_text)
    
    # Display results
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Scores")
        st.write(f"Positive: {scores['pos']:.3f}")
        st.write(f"Neutral: {scores['neu']:.3f}")
        st.write(f"Negative: {scores['neg']:.3f}")
    
    with col2:
        st.subheader("Verdict")
        if scores['compound'] >= 0.05:
            st.success("Positive 😊")
        elif scores['compound'] <= -0.05:
            st.error("Negative 😠")
        else:
            st.info("Neutral 😐")
    
    # Show full review
    with st.expander("See full review"):
        st.write(full_text)