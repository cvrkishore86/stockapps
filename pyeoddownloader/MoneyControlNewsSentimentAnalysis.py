import csv
import time
import requests
from bs4 import BeautifulSoup
# from pattern.en import ngrams

Base_url = "http://www.moneycontrol.com"

# Build a dictionary of companies and their abbreviated names 
companies = {'cadilahealthcare':'CHC','piramalenterprises':'PH05',
             'glenmarkpharma':'GP08','glaxosmithklinepharmaceuticals':'GSK',
             'sunpharmaceuticalindustries':'SPI','lupinlaboratories':'LL',
             'cipla':'C','aurobindopharma':'AP',
             'drreddyslaboratories':'DRL','divislaboratories':'DL03'}

# Create a list of the news section urls of the respective companies 
url_list = ['http://www.moneycontrol.com/company-article/{}/news/{}&durationType=M&duration=1'.format(k,v,v) for k,v in companies.items()]


# Create an empty list which will contain the selected news articles 
List_of_links = []   

# Extract the relevant news articles weblinks from the news section of selected companies
for urls in url_list:
   html = requests.get(urls)
   soup = BeautifulSoup(html.text,'html.parser') # Create a BeautifulSoup object 

   # Retrieve a list of all the links and the titles for the respective links

 
   sub_links = soup.find_all('a', class_='arial11_summ')
   for links in sub_links:
      sp = BeautifulSoup(str(links),'html.parser')  # first convert into a string
      tag = sp.a
      if word1 in tag['title'] or word2 in tag['title'] or word3 in tag['title']:
          category_links = Base_url + tag["href"]
          List_of_links.append(category_links)
          time.sleep(3)
