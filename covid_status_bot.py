import tweepy
import time
import requests
import json

CONSUMER_KEY = 'AAAA'
CONSUMER_SECRET = 'BBBB'
ACCESS_KEY = 'CCCC'
ACCESS_SECRET = 'DDDD'

headers = {
    'x-rapidapi-host': "covid-19-data.p.rapidapi.com",
    'x-rapidapi-key': "EEEE"
    }

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

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
        print(mention.user.screen_name + ' - ' + mention.full_text, flush=True)
        last_seen_id = mention.id
        store_last_seen_id(last_seen_id, FILE_NAME)
        if 'covid' in mention.full_text.lower():
            country = mention.full_text[mention.full_text.index(':') + 1:]
            if 'world' in country.lower():
                url = "https://covid-19-data.p.rapidapi.com/totals"
                try:
                    querystring = {"format":"json"}
                    response = requests.request("GET", url, headers=headers, params=querystring)
                    data = json.loads(response.text[1:-1])
                    time = str(data['lastUpdate']).replace('T', ' ')[0:-6] + ' GMT'
                    reply = (' 𝗗𝗮𝘁𝗮 𝗳𝗼𝗿 𝗪𝗼𝗿𝗹𝗱\n\nTotal Cases: ' + f"{data['confirmed']:,}" +
                            '\nRecovered Cases: ' + f"{data['recovered']:,}" + '\nCurrent Cases: ' +
                            f"{(data['confirmed'] - data['recovered'] - data['deaths']):,}" + 
                            '\nTotal Deaths: ' + f"{data['deaths']:,}" + '\n\nLast updated ' + time)
                    api.update_status('@' + mention.user.screen_name +
                            reply, mention.id)
                except:
                    reply = ' Uh oh! Something went wrong.'
                    api.update_status('@' + mention.user.screen_name +
                            reply, mention.id)
            else:
                url = "https://covid-19-data.p.rapidapi.com/country"
                try:
                    querystring = {"format":"json","name":country}
                    response = requests.request("GET", url, headers=headers, params=querystring)
                    data = json.loads(response.text[1:-1])
                    time = str(data['lastUpdate']).replace('T', ' ')[0:-6] + ' GMT'
                    reply = (' 𝗗𝗮𝘁𝗮 𝗳𝗼𝗿 ' + country.upper() + '\n\nTotal Cases: ' +
                            f"{data['confirmed']:,}" + '\nRecovered Cases: ' + 
                            f"{data['recovered']:,}" + '\nCurrent Cases: ' +
                            f"{(data['confirmed'] - data['recovered'] - data['deaths']):,}" + 
                            '\nTotal Deaths: ' + f"{data['deaths']:,}" + '\n\nLast updated ' + time)
                    api.update_status('@' + mention.user.screen_name +
                            reply, mention.id)
                except:
                    reply = ' Uh oh! Something went wrong.'
                    api.update_status('@' + mention.user.screen_name +
                            reply, mention.id)

while True:
    reply_to_tweets()
    time.sleep(15)
