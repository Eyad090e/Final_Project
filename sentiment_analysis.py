import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
import pandas as pd
import os
nltk.download("vader_lexicon")
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, "tweets_crimes.csv")
tweets_dataset = pd.read_csv(file_path)
analyzer = SentimentIntensityAnalyzer()


def sentiment_detector(tweet):
    sentiment_score = analyzer.polarity_scores(tweet)
    score = sentiment_score["compound"]
    if score < -0.4:
        return "Negative"
    else:
        return "Positive"
    

    
def find_negative_users_tweets(user):
    negative_tweets = []
    tweets = tweets_dataset.loc[tweets_dataset["Author"] == user, "Content"].values
    for tweet in tweets:
            sentiment = sentiment_detector(tweet)
            if sentiment == "Negative":
                negative_tweets.append(tweet)
    return negative_tweets,len(tweets)
        
