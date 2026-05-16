"""Minimal OpenRouter ping test. Run after switching VPN to Global mode."""
import os, requests
from dotenv import load_dotenv

load_dotenv()
key = os.environ.get("OPENROUTER_API_KEY")

# Show what IP Python sees this very moment (sanity)
ip = requests.get("https://ipinfo.io/json", timeout=15).json()
print(f"Python's outbound IP: {ip.get('ip')} / {ip.get('country')} / {ip.get('org', '')[:60]}")

# Ping OpenRouter with minimal request
r = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    },
    json={
        "model": "anthropic/claude-sonnet-4.6",
        "messages": [{"role": "user", "content": "Reply 'pong'."}],
        "max_tokens": 10,
    },
    timeout=30,
)
print(f"\nOpenRouter status: {r.status_code}")
print(f"Body: {r.text[:600]}")
