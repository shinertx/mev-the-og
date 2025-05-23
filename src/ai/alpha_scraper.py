import logging
import requests
import os
import time
import openai

from src.logger import log_event

# If using OpenAI for summarization
openai.api_key = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-4o"

def fetch_twitter_feed(keywords):
    # Use a paid Twitter API or scrape Nitter as fallback (demo)
    tweets = []
    for kw in keywords:
        try:
            resp = requests.get(f"https://nitter.net/search?f=tweets&q={kw}+MEV", timeout=8)
            if resp.status_code == 200:
                tweets.append(resp.text[:1500])  # For demo, real version would parse HTML for tweet text
        except Exception as e:
            log_event(logging.WARNING, f"Twitter fetch fail: {e}", "alpha_scraper")
    return "\n\n".join(tweets)

def fetch_github_feed(repos):
    commits = []
    for repo in repos:
        try:
            resp = requests.get(f"https://api.github.com/repos/{repo}/commits")
            if resp.ok:
                for commit in resp.json()[:2]:
                    msg = commit['commit']['message']
                    commits.append(f"{repo}: {msg}")
        except Exception as e:
            log_event(logging.WARNING, f"Github fetch fail: {e}", "alpha_scraper")
    return "\n\n".join(commits)

def fetch_dune_dashboard(dashboard_id):
    # Dune API is paid, so just simulate for demo
    return f"Simulated Dune dashboard {dashboard_id} result..."

def fetch_telegram_feed(channel):
    # Use Telegram Bot API to get messages, or simulate (demo)
    return f"Simulated latest messages from {channel}"

def summarize_alpha(feed_text):
    prompt = (
        "Summarize any actionable new MEV or DeFi alpha, bridge exploits, sandwich attacks, or arbitrage leaks in this feed. "
        "Output: actionable code/config snippets, or recommendations only."
        f"\n\nFEED:\n{feed_text}"
    )
    try:
        resp = openai.ChatCompletion.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": "You are an adversarial MEV alpha hunter."},
                      {"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=600,
        )
        return resp["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[AlphaScraper] OpenAI failed: {e}"

def run_alpha_scraper():
    # Add relevant alpha keywords and channels
    twitter_keywords = ["bridge exploit", "L2 MEV", "cross-chain arb", "sequencer auction"]
    github_repos = ["flashbots/mev-share", "offchainlabs/arbitrum"]
    dune_dashboards = ["4710832"]  # Dune dashboard IDs
    telegram_channels = ["blockchainalpha", "mevsignals"]

    feed = []
    feed.append(fetch_twitter_feed(twitter_keywords))
    feed.append(fetch_github_feed(github_repos))
    for dash in dune_dashboards:
        feed.append(fetch_dune_dashboard(dash))
    for chan in telegram_channels:
        feed.append(fetch_telegram_feed(chan))

    combined_feed = "\n\n".join(feed)
    summary = summarize_alpha(combined_feed)
    log_event(logging.INFO, f"Summary {summary}", "alpha_scraper")
    return summary

if __name__ == "__main__":
    from src.utils import load_config
    from src.logger import setup_logging
    cfg = load_config("config.yaml")
    setup_logging(cfg)
    log_event(logging.INFO, "Alpha scraper standalone run", "alpha_scraper")
    print(run_alpha_scraper())
