import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import re

def clean_text(text):
    """Cleans extra spaces, newlines, and special characters."""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[[^\]]*\]', '', text)  # remove [1], [2] etc.
    return text.strip()

def scrape_and_summarize(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Try to find main content area
        article = soup.find("article")
        if article:
            paragraphs = article.find_all("p")
        else:
            paragraphs = soup.find_all("p")

        # Extract and clean text
        text = " ".join([clean_text(p.get_text()) for p in paragraphs])
        text = text[:5000]  # keep it concise for summary

        if not text:
            return "⚠️ No readable text found on the page."

        # Simple summarization
        blob = TextBlob(text)
        sentences = blob.sentences

        if len(sentences) > 5:
            summary = " ".join(str(s) for s in sentences[:5])
        else:
            summary = text[:500] + "..."

        return f"📄 Summary:\n{summary}"

    except requests.exceptions.MissingSchema:
        return "❌ Invalid URL format. Please include 'https://'"
    except requests.exceptions.RequestException as e:
        return f"🚨 Network error: {e}"
    except Exception as e:
        return f"⚠️ Unexpected error: {e}"
