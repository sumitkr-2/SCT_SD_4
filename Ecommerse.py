from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import time
import random


def get_title(soup):
    try:
        title = soup.find("span", attrs={"id": 'productTitle'})
        title_string = title.text.strip() if title else ""
    except AttributeError:
        title_string = ""
    return title_string


def get_rating(soup):
    try:
        rating = soup.find("i", attrs={'class': 'a-icon a-icon-star a-star-4-5'})
        if rating:
            rating = rating.string.strip()
        else:
            rating = soup.find("span", attrs={'class': 'a-icon-alt'})
            rating = rating.string.strip() if rating else ""
    except AttributeError:
        rating = ""
    return rating


def get_review_count(soup):
    try:
        review_count = soup.find("span", attrs={'id': 'acrCustomerReviewText'})
        review_count = review_count.string.strip() if review_count else ""
    except AttributeError:
        review_count = ""
    return review_count


def get_availability(soup):
    try:
        available = soup.find("div", attrs={'id': 'availability'})
        available = available.find("span").string.strip() if available else "Not Available"
    except AttributeError:
        available = "Not Available"
    return available


def fetch_page(url, headers, retries=3):
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response
            print(f"Attempt {attempt + 1}: Failed to retrieve the page. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Attempt {attempt + 1}: Request failed with error: {e}")
        time.sleep(random.uniform(1, 5)) 
    return None

if __name__ == '__main__':
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'TE': 'Trailers'
    }

    URL = "https://www.amazon.com/s?k=playstation+4&ref=nb_sb_noss_2"

    
    response = fetch_page(URL, HEADERS)
    
    if response is None:
        print("Failed to retrieve the main page.")
    else:
        soup = BeautifulSoup(response.content, "html.parser")

        
        links = soup.find_all("a", attrs={'class': 'a-link-normal s-no-outline'})
        links_list = ["https://www.amazon.com" + link.get('href') for link in links if link.get('href')]

        d = {"title": [], "rating": [], "reviews": [], "availability": []}

        
        for link in links_list:
            new_response = fetch_page(link, HEADERS)
            if new_response is None:
                print(f"Failed to retrieve the product page: {link}")
                continue
            new_soup = BeautifulSoup(new_response.content, "html.parser")

            d['title'].append(get_title(new_soup))
            d['rating'].append(get_rating(new_soup))
            d['reviews'].append(get_review_count(new_soup))
            d['availability'].append(get_availability(new_soup))

        amazon_df = pd.DataFrame.from_dict(d)
        amazon_df['title'].replace('', np.nan, inplace=True)
        amazon_df = amazon_df.dropna(subset=['title'])
        amazon_df.to_csv("amazon_data.csv", header=True, index=False)
        print("Data saved to amazon_data.csv")
