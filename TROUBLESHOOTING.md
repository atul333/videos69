# Troubleshooting Guide

## Connection Timeout Error

If you're getting a `telegram.error.TimedOut: Timed out` error, this means the bot cannot connect to Telegram's servers.

### Common Causes and Solutions

#### 1. **Network Connectivity Issues**
- **Check your internet connection**: Make sure you have a stable internet connection
- **Test with browser**: Try opening https://telegram.org in your browser
- **Restart your router**: Sometimes a simple router restart helps

#### 2. **Telegram is Blocked in Your Region**
Some countries/ISPs block access to Telegram servers.

**Solution: Use a VPN**
- Install a VPN service (ProtonVPN, NordVPN, etc.)
- Connect to a server in a country where Telegram works
- Run the bot again

#### 3. **Firewall/Antivirus Blocking**
Your firewall or antivirus might be blocking Python from accessing the internet.

**Solution:**
- Temporarily disable your firewall/antivirus
- Add Python to the allowed applications list
- Try running the bot again

#### 4. **Proxy Configuration**
If you're behind a corporate proxy, you may need to configure proxy settings.

**Solution:**
Add proxy configuration to your bot (contact support for help with this)

#### 5. **Incorrect Bot Token**
Double-check your `.env` file has the correct bot token.

**Solution:**
```
BOT_TOKEN=your_actual_bot_token_here
CHANNEL_USERNAME=movie_forward
```

### Quick Fixes to Try

1. **Update python-telegram-bot**:
   ```bash
   pip install --upgrade python-telegram-bot
   ```

2. **Use a VPN** (most common solution for timeout errors)

3. **Check if Telegram is accessible**:
   - Open Telegram Desktop/Mobile app
   - If it works, the issue is with Python/bot configuration
   - If it doesn't work, you need a VPN

4. **Try a different network**:
   - Switch from WiFi to mobile hotspot
   - Try a different internet connection

### Still Having Issues?

If none of the above works:
1. Make sure you're using Python 3.8 or higher
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check if your ISP is blocking Telegram (search online for "Telegram blocked in [your country]")

### Testing Connection

You can test if you can reach Telegram servers by running this in Python:

```python
import requests
try:
    response = requests.get('https://api.telegram.org', timeout=10)
    print("✅ Can reach Telegram servers!")
except Exception as e:
    print(f"❌ Cannot reach Telegram: {e}")
    print("💡 You likely need a VPN")
```

## Other Common Issues

### Bot Not Loading Videos

If the bot starts but doesn't load videos:
1. Make sure the bot is an **admin** in the @movie_forward channel
2. Check that the channel actually has video messages
3. Verify the channel username in `.env` is correct (without @)

### Videos Not Sending to Users

1. Ensure the bot has permission to send messages
2. Check that video message IDs are valid
3. Make sure the channel is public or the bot is a member

---

**Need more help?** Check the bot logs for specific error messages and search for solutions online.
