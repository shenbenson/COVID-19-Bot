import tweepy
import time
import requests
import json

CONSUMER_KEY = 'AAA'
CONSUMER_SECRET = 'BBB'
ACCESS_KEY = 'CCC'
ACCESS_SECRET = 'DDD'
headers = {
    'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
    'x-rapidapi-key': "EEE"
    }

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

url = "https://covid-19-data.p.rapidapi.com/country"
FILE_NAME = 'last_seen_id.txt'

def retrieve_last_seen_id(file_name):
    f_read = open(file_name, 'r')
    last_seen_id = int(f_read.read().strip())
    f_read.close()
    return last_seen_id

def store_last_seen_id(last_seen_id, file_name):
    f_write = open(file_name, 'w')
    f_write.write(str(last_seen_id))
    f_write.close()
    return

def reply_to_tweets():
    print('retrieving and replying to tweets...', flush=True)
    last_seen_id = retrieve_last_seen_id(FILE_NAME)
    mentions = api.mentions_timeline(last_seen_id, tweet_mode='extended')
    for mention in reversed(mentions):
        print(str(mention.id) + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if 'covid' in mention.full_text.lower():
            try:
                country = mention.full_text[mention.full_text.index(':') + 1:]
                querystring = {"format":"json","name":country}
                response = requests.request("GET", url, headers=headers, params=querystring)
                data = json.loads(response.text[1:-1])
                reply = ' Total Cases: ' + str(data['confirmed']) + '\nRecovered Cases: ' + str(data['recovered']) + '\nCurrent Cases: ' + str(data['confirmed'] - data['recovered'] - data['deaths']) + '\nTotal Deaths: ' + str(data['deaths'])
                api.update_status('@' + mention.user.screen_name +
                        reply, mention.id)
            except:
                reply = ' Uh oh! Something went wrong (maybe country not recognized)'
                api.update_status('@' + mention.user.screen_name +
                        reply, mention.id)

while True:
    reply_to_tweets()
    time.sleep(10)
