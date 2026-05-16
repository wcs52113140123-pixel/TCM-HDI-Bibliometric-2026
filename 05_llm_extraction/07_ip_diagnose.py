"""
Day 7 VPN routing diagnostic.

Checks whether Python's HTTP requests are being routed through your VPN.
A common issue on Windows: Clash/V2rayN's "System Proxy" mode only routes
browser traffic. Python's `requests` does NOT read Windows system proxy
settings by default — so API calls go out via your real ISP IP.

Run:
    python 05_llm_extraction/07_ip_diagnose.py
"""
from __future__ import annotations

import os
import sys

import requests

print("="*72)
print(" Python outbound IP diagnostic")
print("="*72)

# Check 1: Environment proxy variables
print("\n[1] Environment proxy variables (does Python see them?)")
for var in ["HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy",
            "ALL_PROXY", "all_proxy", "NO_PROXY"]:
    val = os.environ.get(var)
    print(f"   {var:14s} = {val if val else '(not set)'}")

# Check 2: External IP from Python's perspective
print("\n[2] External IP that Python sees")
for url in ["https://api.ipify.org?format=json",
            "https://ifconfig.me/all.json"]:
    try:
        r = requests.get(url, timeout=10)
        print(f"   {url}\n     → status={r.status_code}, body={r.text[:300]}")
        break
    except Exception as e:
        print(f"   {url}\n     → EXCEPTION: {e}")

# Check 3: Geolocation of that IP
print("\n[3] Geolocation of Python's outbound IP")
try:
    r = requests.get("https://ipapi.co/json/", timeout=10)
    if r.status_code == 200:
        d = r.json()
        print(f"   IP:        {d.get('ip')}")
        print(f"   Country:   {d.get('country_name')} ({d.get('country_code')})")
        print(f"   Region:    {d.get('region')}")
        print(f"   City:      {d.get('city')}")
        print(f"   ISP/Org:   {d.get('org')}")
        cc = d.get("country_code", "")
        if cc in ("CN", "HK", "MO"):
            print(f"\n   ⚠️  Python is going out via {cc} — VPN NOT routing Python traffic")
        else:
            print(f"\n   ✓ Python going out via {cc} — VPN is routing")
    else:
        print(f"   status={r.status_code}, body={r.text[:200]}")
except Exception as e:
    print(f"   EXCEPTION: {e}")

# Check 4: OpenRouter account state (key validity + rate limits)
print("\n[4] OpenRouter /auth/key endpoint")
from dotenv import load_dotenv
load_dotenv()
key = os.environ.get("OPENROUTER_API_KEY")
if not key:
    print("   OPENROUTER_API_KEY not set, skipping")
else:
    try:
        r = requests.get(
            "https://openrouter.ai/api/v1/auth/key",
            headers={"Authorization": f"Bearer {key}"},
            timeout=15,
        )
        print(f"   status={r.status_code}")
        print(f"   body: {r.text[:600]}")
    except Exception as e:
        print(f"   EXCEPTION: {e}")

print("\n" + "="*72)
print(" Interpretation:")
print("="*72)
print("""
 If Check [3] shows Country = CN/HK/MO:
    → Python is bypassing your VPN. Fix one of these ways:
       (a) Enable TUN mode in your VPN client (Clash: 'TUN Mode' toggle,
           V2rayN: Settings → Routing → 'Enable TUN' or use 'V2rayN PAC').
           This routes ALL traffic system-wide.
       (b) Set HTTPS_PROXY environment variable before running Python:
              $env:HTTPS_PROXY="http://127.0.0.1:7890"   # Clash default port
              $env:HTTP_PROXY="http://127.0.0.1:7890"
           Then re-run the benchmark.
       (c) Pass proxies explicitly to the OpenAI/requests client
           (we can patch 03_llm_client.py).

 If Check [3] shows a non-CN country but you still get 403:
    → OpenRouter has flagged your account (probably at signup, by
      payment card BIN). You'd need to contact OR support or use
      a different account.
""")
