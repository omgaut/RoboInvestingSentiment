from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import json
from nltk.sentiment import SentimentIntensityAnalyzer

# Initialize VADER Sentiment Analyzer
sia = SentimentIntensityAnalyzer()

def analyze_sentiment_vader(text):
    """
    Analyzes sentiment using VADER.
    Args:
    - text (str): The text to analyze.
    Returns:
    - float: Sentiment score (compound score).
    """
    sentiment = sia.polarity_scores(text)
    return sentiment["compound"]

def scrape_twitter(ticker, max_tweets=500, output_file="tweets.json"):
    """
    Scrapes Twitter for tweets matching the stock ticker and saves them in a JSON file.
    Args:
    - ticker (str): The stock ticker to search for.
    - max_tweets (int): Maximum number of tweets to scrape.
    - output_file (str): Filename to save the JSON output.
    """
    # Set up Selenium WebDriver
    driver = webdriver.Chrome()
    url = f"https://twitter.com/search?q={ticker}&f=live"
    driver.get(url)

    tweets = []
    num_scrolls = max_tweets // 20  # Estimate based on ~20 tweets per scroll

    # Scroll and load more tweets
    for scroll_count in range(num_scrolls):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Wait for tweets to load

        soup = BeautifulSoup(driver.page_source, "html.parser")
        tweets_html = soup.find_all("article", {"role": "article"})

        # Extract tweet data
        for tweet_html in tweets_html:
            try:
                tweet_text = tweet_html.get_text(separator=" ").strip()

                # Analyze sentiment
                sentiment_score = analyze_sentiment_vader(tweet_text)

                # Append tweet data
                tweets.append({
                    "text": tweet_text,
                    "sentiment_score": sentiment_score
                })
            except Exception as e:
                print(f"Error extracting tweet: {e}")

            # Stop if we've reached the maximum number of tweets
            if len(tweets) >= max_tweets:
                break

        print(f"Scroll {scroll_count + 1}/{num_scrolls} completed. Scraped {len(tweets)} tweets so far.")

        # Stop if we've reached the maximum number of tweets
        if len(tweets) >= max_tweets:
            break

    driver.quit()

    # Sort tweets by sentiment score
    tweets = sorted(tweets, key=lambda x: x["sentiment_score"], reverse=True)

    # Save tweets to a JSON file
    with open(output_file, "w", encoding="utf-8") as jsonfile:
        json.dump(tweets, jsonfile, ensure_ascii=False, indent=4)

    print(f"Scraped {len(tweets)} tweets and saved to {output_file}")

if __name__ == "__main__":
    try:
        # Prompt the user to input a stock ticker
        stock_ticker = input("Enter the stock ticker (e.g., 'AAPL', 'TSLA', 'AMZN'): ").strip().upper()
        print(f"Searching tweets for stock ticker: {stock_ticker}")

        # Scrape Twitter
        scrape_twitter(stock_ticker, max_tweets=500, output_file=f"{stock_ticker}_tweets.json")
        print(f"Scraping completed. Tweets saved in '{stock_ticker}_tweets.json'.")
    except Exception as e:
        print(f"Error: {e}")
