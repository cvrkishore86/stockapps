from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta

from re                   import sub
from nltk.sentiment.vader import SentimentIntensityAnalyzer
starttime=time.time()
from bs4 import BeautifulSoup
import requests
import mechanicalsoup




# It needs NLTK and Vader Analyzer installed
# Write crons to run it automatically at 9:08 everyday
def get_premarket_volume():
    
    top_stocks=["GRASIM","CONCOR","ARVIND","RAMCOCEM","BHARATFORG"]
    print(top_stocks)
    
    return top_stocks

def filter(text):
    text = text.lower().decode('utf-8')
    f = open('D:/code/workspace/NSEOIDownloader/Sentiment'+datetime.now().strftime("%Y-%m-%d")+'.txt', 'a', encoding='utf-8')
    
    print(text,file=f)
    text = sub("[0-9]+", "number", text)
    text = sub("#", "", text)
    text = sub("\n", "", text)
    text = text.replace('$', '@')
    text = sub("@[^\s]+", "", text)
    text = sub("(http|https)://[^\s]*", "", text)
    text = sub("[^\s]+@[^\s]+", "", text)
    text = sub('[^a-z A-Z]+', '', text)
    return text

def similarityScore(s1, s2):
    if len(s1) == 0: return len(s2)
    elif len(s2) == 0: return len(s1)
    v0 = [None]*(len(s2) + 1)
    v1 = [None]*(len(s2) + 1)
    for i in range(len(v0)):
        v0[i] = i
    for i in range(len(s1)):
        v1[0] = i + 1
        for j in range(len(s2)):
            cost = 0 if s1[i] == s2[j] else 1
            v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
        for j in range(len(v0)):
            v0[j] = v1[j]
    return 100-((float(v1[len(s2)])/(len(s1)+len(s2)))*100)

def sentimentScore(texts):
    scores = []
    for text in texts:
        score = SentimentIntensityAnalyzer().polarity_scores(text)["compound"]
        if score != 0: scores.append(score)
    try: return round(sum(scores)/len(scores),3)
    except ZeroDivisionError: return 0

def getmarketsmojo(scrip):
    now = datetime.now()
    fromd = now - timedelta(days=10)
    url='https://www.marketsmojo.com/Stocks?StockId=744293';

    browser = mechanicalsoup.StatefulBrowser()
    browser.open(url)

# Fill-in the search form
    browser.select_form('#search_form_homepage')
    browser["q"] = "MechanicalSoup"
    browser.submit_selected()

# Display the results
    for link in browser.get_current_page().select('a.result__a'):
        print(link.text, '->', link.attrs['href'])



def wakeup():
    
    for stock in get_premarket_volume():
        f = open('D:/code/workspace/NSEOIDownloader/Sentiment'+datetime.now().strftime("%Y-%m-%d")+'.txt', 'a')
        news = getmarketsmojo(stock)

        text='sentiment - Stock: {} score:{}'.format(stock, sentimentScore(news))
        
        print(text,file=f)
        print("------------------------------------"+stock+"-------------------------------",file=f)


if __name__ == '__main__':
    wakeup()
