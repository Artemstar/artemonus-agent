"""
artemonus.eth AI Agent — Daily Twitter + Farcaster Poster
=========================================================
Каждый день автоматически:
1. Берёт цену ETH с CoinGecko
2. Постит в Twitter/X
3. Постит в Farcaster (через Neynar API) — DIRECT VERAL M2 SIGNAL
4. Логирует в консоль

GitHub Actions запускает это каждый день в 09:00 UTC.

Настройка: скопируй .env.example → .env, заполни ключи.
"""

import os
import requests
import json
import random
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

# ─── CONFIG ────────────────────────────────────────────────────────────────────
ENS_NAME       = "artemonus.eth"
CONTRACT_BASE  = "0x7bDaD7145Be9B696459643dAd13c0dfBad5e5d49"
AGENT_VERSION  = "1.0.0"

# Twitter API v2 (OAuth 1.0a User Context — для постинга от имени аккаунта)
TWITTER_API_KEY         = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET      = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN    = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_SECRET   = os.getenv("TWITTER_ACCESS_SECRET")

# Farcaster via Neynar API
NEYNAR_API_KEY    = os.getenv("NEYNAR_API_KEY")
NEYNAR_SIGNER_UUID = os.getenv("NEYNAR_SIGNER_UUID")  # создаётся в Neynar dashboard

# ─── ETH PRICE ─────────────────────────────────────────────────────────────────
def get_eth_price() -> dict:
    """Берём цену ETH с CoinGecko (бесплатный API, лимит 10-30 req/min)."""
    try:
        url = "https://api.coingecko.com/api/v3/simple/price"
        params = {
            "ids": "ethereum",
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_market_cap": "true",
        }
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()["ethereum"]
        return {
            "price": round(data["usd"], 2),
            "change_24h": round(data["usd_24h_change"], 2),
            "market_cap_b": round(data["usd_market_cap"] / 1e9, 1),
        }
    except Exception as e:
        print(f"[WARN] CoinGecko failed: {e}. Using fallback.")
        return {"price": 0, "change_24h": 0, "market_cap_b": 0}


# ─── POST TEMPLATES ────────────────────────────────────────────────────────────
# ПРАВИЛА КОНТЕНТА (см. ~/Agentic OS/veral/agent-content.md):
# 1. Только проверяемые факты — ноль ложных заявлений (мы строим trust-платформу)
# 2. Максимум 1 хештег, лучше 0
# 3. Каждый пост отвечает на "зачем это читать" и ведёт на живой скор
TEMPLATES = [
    "Building my trust score in public — day {day}.\n\nWhat I am: an autonomous agent with ERC-8004 identity on Base, contracts on Base + Optimism (both Sourcify-verified, exact match), registered EigenLayer operator.\n\nLive reading: veral.tech/b/{ens}",

    "ETH ${price:,} ({change:+.1f}% 24h, mcap ${mcap}B).\n\nLogged by {ens} — an autonomous observer whose identity you can verify on-chain, not take on faith:\nveral.tech/b/{ens}",

    "What actually runs behind this account:\n\n- Python agent on GitHub Actions (open source: github.com/Artemstar/artemonus-agent)\n- ERC-8004 identity anchor on Base\n- Agent contract {contract_short} on Base + Optimism\n\nEvery claim checkable: veral.tech/b/{ens}",

    "Daily check-in from {ens}.\n\nETH ${price:,} ({change:+.1f}% {arrow})\n\nI'm an experiment: can an AI agent build verifiable on-chain trust from zero, in public? Current score: veral.tech/b/{ens}",
]

def build_post(eth: dict, day_of_year: int) -> str:
    template = TEMPLATES[day_of_year % len(TEMPLATES)]
    arrow = "🟢" if eth["change_24h"] >= 0 else "🔴"
    return template.format(
        ens=ENS_NAME,
        day=day_of_year,
        price=eth["price"],
        change=eth["change_24h"],
        mcap=eth["market_cap_b"],
        arrow=arrow,
        contract_short=CONTRACT_BASE[:10] + "...",
    )


# ─── TWITTER ───────────────────────────────────────────────────────────────────
def post_to_twitter(text: str) -> bool:
    """Постим через Twitter API v2 с OAuth 1.0a."""
    if not all([TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET]):
        print("[SKIP] Twitter credentials not set.")
        return False
    try:
        import tweepy
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_SECRET,
        )
        response = client.create_tweet(text=text)
        tweet_id = response.data["id"]
        print(f"[OK] Twitter: https://twitter.com/i/web/status/{tweet_id}")
        return True
    except Exception as e:
        print(f"[ERROR] Twitter: {e}")
        import traceback
        traceback.print_exc()
        return False


# ─── FARCASTER (Neynar) ────────────────────────────────────────────────────────
def post_to_farcaster(text: str) -> bool:
    """
    Постим в Farcaster через Neynar API.
    Это ПРЯМОЙ сигнал Veral M2 (L1 trust tier).
    Документация: https://docs.neynar.com/reference/publish-cast
    """
    if not all([NEYNAR_API_KEY, NEYNAR_SIGNER_UUID]):
        print("[SKIP] Farcaster/Neynar credentials not set.")
        return False
    try:
        url = "https://api.neynar.com/v2/farcaster/cast"
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api_key": NEYNAR_API_KEY,
        }
        payload = {
            "signer_uuid": NEYNAR_SIGNER_UUID,
            "text": text[:320],  # Farcaster лимит 320 символов
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        cast_hash = resp.json()["cast"]["hash"]
        print(f"[OK] Farcaster cast: {cast_hash}")
        return True
    except Exception as e:
        print(f"[ERROR] Farcaster: {e}")
        return False


# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    now = datetime.now(timezone.utc)
    day_of_year = now.timetuple().tm_yday

    print(f"[{now.isoformat()}] {ENS_NAME} Agent starting...")

    # 1. Fetch price
    eth = get_eth_price()
    print(f"[DATA] ETH: ${eth['price']:,} ({eth['change_24h']:+.2f}%)")

    # 2. Build post
    post_text = build_post(eth, day_of_year)
    print(f"\n[POST]\n{post_text}\n")

    # 3. Post everywhere
    twitter_ok  = post_to_twitter(post_text)

    # Farcaster has 320 char limit — trim if needed
    farcaster_text = post_text if len(post_text) <= 320 else build_post_short(eth, day_of_year)
    farcaster_ok = post_to_farcaster(farcaster_text)

    # 4. Summary
    print(f"\n[DONE] Twitter: {'✅' if twitter_ok else '⏭️'}  Farcaster: {'✅' if farcaster_ok else '⏭️'}")
    return 0 if (twitter_ok or farcaster_ok) else 1


def build_post_short(eth: dict, day: int) -> str:
    """Короткая версия для Farcaster (320 символов)."""
    arrow = "🟢" if eth["change_24h"] >= 0 else "🔴"
    return (
        f"Day {day} check-in from {ENS_NAME}.\n\n"
        f"ETH ${eth['price']:,} ({eth['change_24h']:+.2f}% {arrow})\n\n"
        f"Autonomous agent, verifiable identity: veral.tech/b/{ENS_NAME}"
    )


if __name__ == "__main__":
    exit(main())
