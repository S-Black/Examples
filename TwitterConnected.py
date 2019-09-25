#-----------------------------------
# Twitter Royal Mail sentiment analysis
#
# v1: 22/09/19
# by: SB
#-----------------------------------

# Libraries
#--------------
from nltk.twitter import Twitter,Query, Streamer, Twitter, TweetViewer, TweetWriter, credsfromfile
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import string
import re
import json
from pprint import pprint
import sys

# Functions
#------------------
def frequencyDistribution(data):
    return {i: data.count(i) for i in data}


#LIVE twitter feed
#------------------
#get 10 twitter messages with #Primark
tw = Twitter()
tw.tweets(keywords='#royalmail', stream=False, limit=10)

brand='royalmail'

#API keys
#------------------------
oauth = credsfromfile()
client = Query(**oauth)
tweets = client.search_tweets(keywords=brand, limit=20000)
tweet = next(tweets)
pprint(tweet, depth=1)

#make sure tweets can be encoded
non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
#print(x.translate(non_bmp_map))

# Sentiment analysis
#-------------------------------
analyzer = SentimentIntensityAnalyzer() #vadersentiment object

Data=[]
Words=[]
Label=[]

#write to file
myfile= open(brand+'.txt', 'w')
myfile.write('Date,pos score,neg score,label \n')

stops = set(stopwords.words("english"))
#i=0
#display each tweet text
for tweet in tweets:
    line=tweet['text']
    #i+=1
    #print(i)
    #keep only english tweets
    if tweet['lang']=='en':
        #print(tweet['retweet_count'])
        #print(ascii(tweet['text']))
        #print(tweet['text'].translate(non_bmp_map))
        #print(codecs.decode(tweet['text'],'raw_unicode_escape'))

        #filter out retweets for competitions and stuff that distort the picture
        if line[:2].translate(non_bmp_map)!= 'RT':
            #print(tweet['created_at'])
            #print(line.translate(non_bmp_map))

            analysis = TextBlob(line) #textblob object
            vs = analyzer.polarity_scores(line) #dictionary

            #Create list with sentiment scores
            Data.append([analysis.sentiment.polarity,analysis.sentiment.subjectivity,list(vs.values())[0],list(vs.values())[1],list(vs.values())[2]])

            #Create a list with pos (1)/neg (-1)/neutral (0) label
            if list(vs.values())[2]>list(vs.values())[0]:
                t=1
                Label.append(1)
            elif list(vs.values())[2]<list(vs.values())[0]:
                t=-1
                Label.append(-1)
                print(line.translate(non_bmp_map))
            else:
                t=0
                Label.append(0)

            #write data to file
            myfile.write(tweet['created_at']+","+str(list(vs.values())[2])+","+str(list(vs.values())[0])+","+str(t)+"\n")

            #Create list with main words associated with each post
            Nouns =analysis.noun_phrases
            #print(Nouns)
            TempWords=[]
            for word in Nouns:
                word=str(word)
                #remove any punctuation and characters such as @
                word=re.sub(r'[^\w\s]','',word, re.UNICODE)
                #split into separate words and remove any spaces
                tempword = word_tokenize(word.lower())
                #remove stop words that have no meaning
                meaningful_words = [w for w in tempword if not w in stops]
                #Add to list
                TempWords+=tempword

            Words.append(TempWords)

myfile.close()

#Count frequency of pos, neutral and negative sentiment
Sentiment=frequencyDistribution(Label)
print(Sentiment)

#Look into popular words associated with pos/neg sentiment
PosWords=[]
NegWords=[]
for i in range(len(Words)):
    if Label[i]==1:
        PosWords+=(Words[i])
    if Label[i]==-1:
        NegWords+=(Words[i])

PosWordsFreq=frequencyDistribution(PosWords)
print(sorted(PosWordsFreq.items(), key=lambda x: x[1]))
with open(brand+'PosWords.txt', 'w') as f:
    json.dump(sorted(PosWordsFreq.items(), key=lambda x: x[1]), f)

NegWordsFreq=frequencyDistribution(NegWords)
print(sorted(NegWordsFreq.items(), key=lambda x: x[1]))
with open(brand+'NegWords.txt', 'w') as f:
    json.dump(sorted(NegWordsFreq.items(), key=lambda x: x[1]), f)
