from flask import Flask, render_template, request,session
import mysql.connector
import random
from datetime import datetime
import requests
import os
from datetime import date
from neg_words import extract_negative_words
import joblib
import re

def cleanTweet(tweet):
    tweet = re.sub(r"[^a-z\s]", "", tweet)
    tweet = re.sub(r"\s+", " ", tweet)
    tweet = tweet.strip()
    tweet = tweet.lower()
    return tweet

app = Flask(__name__)

app.secret_key = '12345678'
conf = {
     "host":'localhost',
    "user":'root',
    "password":'',
    "database":'tweets_cc'
}

number_of_time_without_login = 0

@app.route('/signup', methods=["GET"])
def signup():
    return render_template('signup.html')

@app.route('/login', methods=["GET"])
def login():
    return render_template('login.html')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/logout')
def logout():
    del session["user_id"]
    return render_template('login.html')

@app.route('/login_proccess',methods=["POST"])
def login_proccess():
    conn = mysql.connector.connect(**conf)
    cursor = conn.cursor(dictionary=True)


    email = request.form["email"]
    password = request.form["password"]
    cursor.execute("SELECT id,blocked FROM users WHERE email = %s and password = %s", (email,password))
    account = cursor.fetchone()
    cursor.close()
    conn.close()
    print(account)
    if account:
        if account['blocked']:
            message = "This account is blocked due to cybercrime tweet inserting"
            return render_template('login.html',message=message)
    
        session["user_id"] = account["id"]
        print("$$$$$$$$$$",session["user_id"])
        return render_template('home.html')
    else:
        message = "Failed to login, Please try again"
        return render_template('login.html',message=message)
    
@app.route('/signup_proccess',methods=["POST"])
def signup_proccess():
    conn = mysql.connector.connect(**conf)
    cursor = conn.cursor(dictionary=True)
    email = request.form["email"]
    password = request.form["password"]
    name = request.form["fullname"]
    sql = "INSERT INTO users (fullname, email,password) VALUES (%s, %s,%s)"
    cursor.execute(sql, (name, email,password))
    conn.commit()
    cursor.close()
    conn.close()
    return render_template('login.html')


@app.route('/analyze_withoutlogin')
def analyze_withoutlogin():
        global number_of_time_without_login
        print("*********",number_of_time_without_login)
        if number_of_time_without_login>=1:
            return render_template('access_method.html',message="Please login first, you exceed the allowed analysis processes without login")
        number_of_time_without_login +=1
        session["once"] = 1
        return render_template('analyse.html')

@app.route('/access_method')
def access_method():
    if "user_id" not in session:
        return render_template('access_method.html')
    else:
        return render_template('analyse.html')


@app.route('/analyse')
def analyse():
    if "user_id" in session:
        return render_template('analyse.html')
    else:
        return render_template('login.html')
    


@app.route('/analyse_username',methods=["GET"])
def analyse_username():
    username = request.args["username"]
    crime_words,tweets_number,negative_tweets_number,neg_tweets = extract_negative_words(username)
    print(tweets_number)
    negative_tweets_rate = negative_tweets_number/tweets_number
    print("@@@",len(neg_tweets))
    print(neg_tweets)
    if "user_id" in session:
        conn = mysql.connector.connect(**conf)
        cursor = conn.cursor(dictionary=True)
        user_id  =  session["user_id"]
        t_count = tweets_number
        rate = negative_tweets_rate
        sql = "INSERT INTO history (user_id, t_counts,crime_rate,username) VALUES (%s, %s,%s,%s)"
        cursor.execute(sql, (user_id, t_count,rate,username))
        conn.commit()
    return render_template('results.html',message = {
                                "username":username,
                                "tweets_num":tweets_number,
                                "negative_rate":negative_tweets_rate,
                                "crime_words":crime_words,
                                "neg_tweets":neg_tweets,
                                "hist":"no_hist"
                                }
            )



@app.route('/history')
def history():
    if "user_id" in session:
        user_id = session["user_id"]
        conn = mysql.connector.connect(**conf)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id,username,t_counts,crime_rate FROM history WHERE user_id = %s", (user_id,))
        hist = cursor.fetchall()
        cursor.close()
        conn.close()
        print(hist)
        return render_template('history.html',hist=hist)
    else:
        return render_template('login.html')
    

@app.route('/detect_emotion')
def detect_emotion():
    if "user_id" in session:
        user_id = session["user_id"]
        origin_tweet = request.args.get("tweet")
        extractor_emotion = joblib.load("emotion_sentiments/data_vectorizer.pkl")
        svm_emotion = joblib.load("emotion_sentiments/svm_model.pkl")

        extractor_detection = joblib.load("cybercrime_users_blocking/data_vectorizer.pkl")
        svm_detection = joblib.load("cybercrime_users_blocking/svm_model.pkl")
        tweet = cleanTweet(origin_tweet)
        X = extractor_detection.transform([tweet])
        cyber_crime = int(svm_detection.predict(X)[0])
        if cyber_crime == 1:
            print("This tweet contains cybercrime")
            conn = mysql.connector.connect(**conf)
            cursor = conn.cursor(dictionary=True)
            sql = "UPDATE users set blocked=%s where id=%s"
            cursor.execute(sql, (1, user_id))
            conn.commit()
            conn.close()
            message = "This account is blocked due to cybercrime tweet inserting"
            return render_template('login.html',message=message)
        else:
            print("This tweet does not contain cybercrime")
        tweet = cleanTweet(origin_tweet)
        X = extractor_emotion.transform([tweet])
        emotion_code = int(svm_emotion.predict(X)[0])
        emotions = {
            0:"sadness",
            1:"joy",
            2: "love",
            3:"anger",
            4:"fear",
            5:"surprise"
        }
        print(emotions[emotion_code])
        return render_template('results_emotion.html',message={"label":emotions[emotion_code],"emotion_tweet":origin_tweet})
    else:
        return render_template('login.html')
    


app.run()