import re
import nltk
from sentiment_analysis import find_negative_users_tweets
from nltk.corpus import  opinion_lexicon
from nltk.tokenize import word_tokenize
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('opinion_lexicon')
nltk.download('punkt')

stop_words = set(nltk.corpus.stopwords.words('english'))
negative_words = set(opinion_lexicon.negative())

def preprocess_tweets(tweet):
    tweet = re.sub(r'http\S+|www.\S+', '', tweet) 
    tweet = re.sub(r'@\w+', '', tweet) 
    tweet = re.sub(r'[^a-zA-Z\s]', '', tweet.lower())
    words = word_tokenize(tweet)
    return words

#"katyperry"

def extract_negative_words(username):
    tweets,tweets_number = find_negative_users_tweets(username)
    crime_words = []
    for tweet in tweets:
        words = preprocess_tweets(tweet)
        crime_word = [word for word in words if word in negative_words]
        if crime_word:
            crime_words.append(crime_word)
    return crime_words,tweets_number,len(tweets),tweets


