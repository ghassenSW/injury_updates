import requests
import numpy as np
import pandas as pd
import time
import tweepy
from datetime import datetime

bearer_token = "AAAAAAAAAAAAAAAAAAAAAKSxwAEAAAAAvgGs4WP4xJdgJv19PvRPPsQXyLw%3DXRXe2GQelKx3ERIdtMBV8VGiKxXNUYTWA1rSxKPq0ewwydL71e"
consumer_key = "5nVBklpC137d8SlUnsndAlflO"
consumer_secret = "8jdg9r2AFP7LLj0OWxHwrc2fPYa2xvqt479aaBDw4yNhGSQGTN"
access_token = "858082603861254144-LmgwViCJtyAnA7JYIfWPAIjuZPP6Vfm"
access_token_secret = "wMYjUjkEJ4KQWu1V4KJI0mdYrIqlRQvJN6m1Nk9cjB9gW"

def url_to_df(url,key=None):
  response = requests.get(url)
  if response.status_code == 200:
      data = response.json()
      if key!=None:
        df=pd.DataFrame(data[key])
      else:
        df=pd.DataFrame(data)
      return df
  else:
      print(f"Error: {response.status_code}")

def prepare(df):
  df['full_name']=df['first_name']+' '+df['second_name']
  df['team']=df['team'].map(map.iloc[0])
  df=df[['chance_of_playing_next_round','team','full_name','news']]
  df['chance_of_playing_next_round']=df['chance_of_playing_next_round'].fillna(101)
  df['news']=df['news'].fillna('')

  return df

def text_to_tweet(players):
    tweet_text=''
    for index,row in players.iterrows():
        tweet_text+='🚨 Injury Updates\n'
        player_name=row['full_name']
        team_name=row['team']
        tweet_text+=f'👟 Player : {player_name} ({team_name})\n'
        if(row['chance_of_playing_next_round']==100):
            tweet_text+=f'🤕 Update: Availability is now 100%\n'
        else:
            stat=row['news']
            tweet_text+=f'🤕 Update: {stat}\n'
        tweet_text+='\n|'
    tweet_text=tweet_text.strip('\n|')
    return tweet_text

def split_text_into_tweets(text, limit=280):
    lines = text.split('|')
    tweets = []
    current_tweet = ""

    for line in lines:
        if len(current_tweet) + len(line) + 1 <= limit:
            current_tweet += f"{line}"
        else:
            tweets.append(current_tweet.strip())
            current_tweet = f"{line}"
    if current_tweet:
      tweets.append(current_tweet.strip('\n'))  
    return tweets



url='https://fantasy.premierleague.com/api/bootstrap-static/'
teams=url_to_df(url,'teams')
map=dict(zip(teams['id'],teams['name']))
map=pd.DataFrame(map,index=[0])
present_fixtures=url_to_df('https://fantasy.premierleague.com/api/fixtures/?future=1')
num_gameweek=present_fixtures['event'].min()
current_date = datetime.now().date()

new_df=url_to_df('https://fantasy.premierleague.com/api/bootstrap-static/','elements')
old_date=datetime.now().date()-pd.Timedelta(days=1)
old_df=pd.read_csv(r"C:\Users\ghass\Downloads\players_2024-10-03.csv")
new=prepare(new_df)
old=prepare(old_df)
conditions=new[['chance_of_playing_next_round','news']]!=old[['chance_of_playing_next_round','news']]
first_condition=new[conditions['chance_of_playing_next_round']]
second_condition=new[conditions['news']]
players = pd.concat([first_condition, second_condition], axis=0, ignore_index=True)
players = players.drop_duplicates()
tweet_text=text_to_tweet(players)

bearer_token = "AAAAAAAAAAAAAAAAAAAAAKSxwAEAAAAAvgGs4WP4xJdgJv19PvRPPsQXyLw%3DXRXe2GQelKx3ERIdtMBV8VGiKxXNUYTWA1rSxKPq0ewwydL71e"
consumer_key = "5nVBklpC137d8SlUnsndAlflO"
consumer_secret = "8jdg9r2AFP7LLj0OWxHwrc2fPYa2xvqt479aaBDw4yNhGSQGTN"
access_token = "858082603861254144-LmgwViCJtyAnA7JYIfWPAIjuZPP6Vfm"
access_token_secret = "wMYjUjkEJ4KQWu1V4KJI0mdYrIqlRQvJN6m1Nk9cjB9gW"

client = tweepy.Client(bearer_token=bearer_token, consumer_key=consumer_key, consumer_secret=consumer_secret,
                       access_token=access_token, access_token_secret=access_token_secret)
if len(tweet_text) <=280:
  response = client.create_tweet(text=tweet_text)
  print(f"Posted single tweet:--------------------------------------------------------------------------------\n{tweet_text}")
else:
  tweets = split_text_into_tweets(tweet_text)
  last_tweet = client.create_tweet(text=tweets[0])
  print(f"Posted tweet:--------------------------------------------------------------------------------------\n{tweets[0]}")
  for tweet in tweets[1:]:
      last_tweet = client.create_tweet(text=tweet, in_reply_to_tweet_id=last_tweet.data['id'])
      print(f"Posted tweet in thread:------------------------------------------------------------------------\n{tweet}")