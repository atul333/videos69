"""
Simple script to test if you can connect to Telegram servers.
Run this before running the bot to diagnose connection issues.
"""

import requests
import sys

print("Testing connection to Telegram servers...\n")

# Test 1: Basic internet connectivity
print("Test 1: Checking internet connection...")
try:
    response = requests.get('https://www.google.com', timeout=5)
    print("[OK] Internet connection is working\n")
except Exception as e:
    print(f"[FAIL] No internet connection: {e}")
    print("TIP: Please check your internet connection and try again\n")
    sys.exit(1)

# Test 2: Telegram API accessibility
print("Test 2: Checking Telegram API accessibility...")
try:
    response = requests.get('https://api.telegram.org', timeout=10)
    print("[OK] Telegram API is accessible!")
    print("[OK] You should be able to run the bot\n")
except requests.exceptions.Timeout:
    print("[FAIL] Timeout connecting to Telegram API")
    print("TIP: Telegram servers might be blocked in your region")
    print("TIP: Solution: Use a VPN and try again\n")
    sys.exit(1)
except Exception as e:
    print(f"[FAIL] Cannot reach Telegram API: {e}")
    print("TIP: This could be a firewall/proxy issue")
    print("TIP: Try using a VPN or check your firewall settings\n")
    sys.exit(1)

# Test 3: Check bot token
print("Test 3: Checking bot token...")
try:
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    bot_token = os.getenv('BOT_TOKEN')
    
    if not bot_token:
        print("[FAIL] BOT_TOKEN not found in .env file")
        print("TIP: Make sure you have a .env file with BOT_TOKEN=your_token\n")
        sys.exit(1)
    
    # Test the token
    response = requests.get(f'https://api.telegram.org/bot{bot_token}/getMe', timeout=10)
    
    if response.status_code == 200:
        bot_info = response.json()
        if bot_info.get('ok'):
            print(f"[OK] Bot token is valid!")
            print(f"[OK] Bot username: @{bot_info['result']['username']}")
            print(f"[OK] Bot name: {bot_info['result']['first_name']}\n")
        else:
            print("[FAIL] Invalid bot token")
            print("TIP: Check your BOT_TOKEN in the .env file\n")
            sys.exit(1)
    else:
        print(f"[FAIL] Error validating bot token: {response.status_code}")
        print("TIP: Check your BOT_TOKEN in the .env file\n")
        sys.exit(1)
        
except Exception as e:
    print(f"[FAIL] Error checking bot token: {e}\n")
    sys.exit(1)

print("=" * 50)
print("[SUCCESS] ALL TESTS PASSED!")
print("[SUCCESS] You can now run the bot with: python bot.py")
print("=" * 50)

