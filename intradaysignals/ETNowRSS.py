import feedparser


d = feedparser.parse('http://economictimes.indiatimes.com/markets/stocks/rssfeeds/2146842.cms')

for post in d.entries:

    print(post.title , post.link ,post.published)