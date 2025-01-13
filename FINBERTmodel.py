from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
from transformers import pipeline

# Initialize FinBERT
finbert = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")

def analyze_sentiment_finbert(text):

    #Analyzes sentiment using FinBERT.

    try:
        result = finbert(text)
        return result[0]['label']
    except Exception as e:
        print(f"Error analyzing sentiment: {e}")
        return "NEUTRAL"

def scrape_twitter(ticker, max_tweets=500, output_file="tweets.json"):

    #Scrapes Twitter for tweets matching the stock ticker and saves them in a JSON file.

    #Set up Selenium
    driver = webdriver.Chrome()
    url = f"https://twitter.com/search?q={ticker}&f=live"
    driver.get(url)

    tweets = []
    num_scrolls = max_tweets // 20 #20 per scroll assumed

    #load more tweets
    for scroll_count in range(num_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        tweets_html = soup.find_all("article", {"role": "article"})

        #Extract tweet info
        for tweet_html in tweets_html:
            try:
                tweet_text = tweet_html.get_text(separator=" ").strip()

                #Analyze sentiment
                sentiment_label = analyze_sentiment_finbert(tweet_text)

                #Append tweet data
                tweets.append({
                    "text": tweet_text,
                    "sentiment": sentiment_label
                })
            except Exception as e:
                print(f"Error extracting tweet: {e}")


            if len(tweets) >= max_tweets:
                break

        print(f"Scroll {scroll_count + 1}/{num_scrolls} completed. Scraped {len(tweets)} tweets so far.")

        if len(tweets) >= max_tweets:
            break

    driver.quit()

    # Save tweets to a JSON file
    with open(output_file, "w", encoding="utf-8") as jsonfile:
        json.dump(tweets, jsonfile, ensure_ascii=False, indent=4)

    print(f"Scraped {len(tweets)} tweets and saved to {output_file}")

def main():
    try:
        # Prompt the user to input a stock ticker
        stock_ticker = input("Enter the stock ticker: ").strip().upper()
        print(f"Searching tweets for stock ticker: {stock_ticker}")

        # Scrape Twitter
        scrape_twitter(stock_ticker, max_tweets=500, output_file=f"{stock_ticker}_tweets.json")
        print(f"Scraping completed. Tweets saved in '{stock_ticker}_tweets.json'.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
