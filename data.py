import requests
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import json
import os

def fetch_latest_articles(sitemap_url):
    response = requests.get(sitemap_url)
    if response.status_code == 200:
        root = ET.fromstring(response.content)
        articles = root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}url")

        latest_articles_data = []
        for article in articles[:10]:  # Get the latest 10 articles
            loc = article.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text
            response = requests.get(loc)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                last_updated = soup.find(class_='posted-on').find('time').text.strip()
                post_title = fetch_and_analyze_post_title(soup)
                if post_title:
                    category = determine_category(post_title)
                else:
                    category = "Other"
                article_data = {
                    'Last Updated': last_updated,
                    'Category': category
                }
                if post_title:
                    article_data['Title'] = post_title

                latest_articles_data.append(article_data)

        # Storing data in a JSON file
        with open('latest_articles.json', 'w') as json_file:
            json.dump(latest_articles_data, json_file, indent=4)

        print("Latest 10 articles data stored in 'latest_articles.json' file.")
    else:
        print("Failed to fetch sitemap XML.")

def fetch_and_analyze_post_title(soup):
    post_title_tag = soup.find('h1', class_='entry-title')
    if post_title_tag:
        post_title = post_title_tag.text.strip()
        keywords = ['Recruitment 2024', 'Notification', 'Admit Card 2024', 'Result']
        for keyword in keywords:
            if keyword in post_title:
                return post_title.split(keyword)[0] + keyword
    return None

def determine_category(title):
    if "Recruitment 2024" in title:
        return "Recruitment"
    elif "Notification" in title:
        return "Notification"
    elif "Admit Card 2024" in title:
        return "Admit Card"
    elif "Result" in title:
        return "Result"
    else:
        return "Other"

if __name__ == "__main__":
    sitemap_url = os.environ('geturlid')
    if sitemap_url:
        fetch_latest_articles(sitemap_url)
    else:
        print("Sitemap URL is not provided in the environment variable.")
