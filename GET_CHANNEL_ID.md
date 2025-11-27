# How to Get Channel ID for Private Channels

## Problem
Private channels with invite links (like `https://t.me/+Pkij1IcrzhJjMDBl`) cannot be accessed using the `@+link` format. You need the numeric chat ID instead.

## Solution: Get the Numeric Channel ID

### Method 1: Using @userinfobot (Recommended)

1. **Add @userinfobot to your channel**
   - Open your channel
   - Click "Add Members"
   - Search for `@userinfobot`
   - Add it to the channel

2. **Forward a message from your channel to @userinfobot**
   - Go to your channel
   - Forward any message to @userinfobot
   - The bot will reply with the channel ID

3. **Copy the ID**
   - Look for "Chat" or "Forward from chat"
   - Copy the number (e.g., `-1002433066913`)
   - This is your channel ID!

4. **Update bot.py**
   ```python
   MANDATORY_CHANNEL = -1002433066913  # Your channel ID
   ```

### Method 2: Using @getidsbot

1. **Forward a message from your channel to @getidsbot**
2. The bot will reply with the channel ID
3. Copy and use it in your code

### Method 3: Using Your Bot

1. **Add your bot to the channel as admin**
2. **Send a message in the channel**
3. **Check bot logs** - it will show the chat ID

### Method 4: Manual API Call

```python
# Temporary code to get channel ID
import asyncio
from telegram import Bot

async def get_channel_id():
    bot = Bot(token="YOUR_BOT_TOKEN")
    updates = await bot.get_updates()
    for update in updates:
        if update.channel_post:
            print(f"Channel ID: {update.channel_post.chat.id}")

asyncio.run(get_channel_id())
```

## Important Notes

### Format Differences

**Public Channels:**
```python
MANDATORY_CHANNEL = "@channelname"  # Use @ + username
```

**Private Channels:**
```python
MANDATORY_CHANNEL = -1002433066913  # Use numeric ID
```

### Channel ID Format

- Always starts with `-100`
- Followed by more digits
- Example: `-1002433066913`
- **Must be a number, not a string!**

### Common Mistakes

❌ **Wrong:**
```python
MANDATORY_CHANNEL = "@+Pkij1IcrzhJjMDBl"  # Won't work!
MANDATORY_CHANNEL = "https://t.me/+Pkij1IcrzhJjMDBl"  # Won't work!
MANDATORY_CHANNEL = "+Pkij1IcrzhJjMDBl"  # Won't work!
```

✅ **Correct:**
```python
MANDATORY_CHANNEL = -1002433066913  # Works!
```

## Current Configuration

```python
# In bot.py
MANDATORY_CHANNEL = -1002433066913  # Numeric ID for private channel
MANDATORY_CHANNEL_LINK = "https://t.me/+Pkij1IcrzhJjMDBl"  # Invite link for users
```

## Testing

After updating the channel ID:

1. **Restart the bot**
2. **Send /start**
3. **Should work without "Chat not found" error**

If you still get errors:
- Make sure bot is admin in the channel
- Make sure the ID is correct
- Make sure it's a number, not a string

## Summary

- ✅ Use numeric ID for private channels
- ✅ Use @username for public channels
- ✅ Get ID from @userinfobot or @getidsbot
- ✅ Format: `-1002433066913` (number, not string)
- ✅ Bot must be admin in channel
