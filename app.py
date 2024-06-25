import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
import urllib.request
import argparse
from unidecode import unidecode
import os
import time
import re 

class ArticleScraper:
    def __init__(self, base_url, search_term):
        self.base_url = base_url
        self.search_term = search_term
        self.article_links = []
        self.article_names = []
        self.download_links = []

    def search_articles(self,page_num):
        for i in range(1, page_num):
            link = f"{self.base_url}{i}?q={quote_plus(unidecode(self.search_term))}&section=articles"
            r = requests.get(link)
            soup = BeautifulSoup(r.content, "html.parser")
            titles = soup.find_all("h5", {"class": "card-title"})
            for title in titles:
                a = title.find("a")
                self.article_links.append(a.get("href"))
                self.article_names.append(re.sub(r'^\s+|\s+$',"",a.text))

    def get_download_links(self):
        for i in range(0, len(self.article_links)):
            r2 = requests.get(self.article_links[i])
            soup2 = BeautifulSoup(r2.content, "html.parser")
            try:
                s2 = soup2.find("div", {"id": "article-toolbar"}).find("a").get("href")
                url = f"https://dergipark.org.tr{s2}"
                self.download_links.append(url)
                time.sleep(1)
            except AttributeError:
                print(f"Could not retrieve the link for article {i+1}")

    def download_articles(self, path):
        if not os.path.exists(path):
            print("Path not found, creating it.")
            os.makedirs(path)

        for k in range(0, len(self.download_links)):
            try:
                urllib.request.urlretrieve(self.download_links[k], os.path.join(path, f"{k+1}-{self.article_names[k]}.pdf"))
            except Exception as e:
                print(f"Error downloading file {self.article_names[k]}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search_term", help="search article subject", required=True)
    parser.add_argument("-n", "--page_number", help="search page number", type=int, default=2)
    args = parser.parse_args()
    search_term = args.search_term
    page_num = args.page_number

    print(search_term)

    path = "https://dergipark.org.tr/tr/search/"
    scraper = ArticleScraper(path, search_term)
    scraper.search_articles(page_num)
    scraper.get_download_links()
    path = os.path.join(os.getcwd(),search_term)
    scraper.download_articles(path)