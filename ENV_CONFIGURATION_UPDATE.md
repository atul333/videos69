# Environment Configuration Update

## Change Summary
**Date:** December 13, 2025

### What Changed
Moved bot-specific configuration values from `video69_bot.py` to `.env` file for easier management across multiple bots.

## Configuration Values Moved to .env

The following values are now read from environment variables:

1. **CHANNEL_ID** - Your Telegram channel ID
2. **BOT_USERNAME** - Your bot's username
3. **MAX_MESSAGE_ID** - Maximum message ID in your channel

## How to Update Your .env File

Add these three lines to your `.env` file:

```env
# Bot Configuration
BOT_TOKEN=your_bot_token_here
CHANNEL_USERNAME=your_channel_username

# New Configuration (add these)
CHANNEL_ID=-1003329285677
BOT_USERNAME=Test_videos69_bot
MAX_MESSAGE_ID=2500
```

## Complete .env File Example

Here's what your complete `.env` file should look like:

```env
# Telegram Bot Token
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Channel Configuration
CHANNEL_USERNAME=your_channel_username
CHANNEL_ID=-1003329285677

# Bot Configuration
BOT_USERNAME=Test_videos69_bot
MAX_MESSAGE_ID=2500
```

## Benefits

### Before (Hardcoded in video69_bot.py)
```python
CHANNEL_ID = -1003067861005  # Had to edit code file
BOT_USERNAME = "Test_videos69_bot"  # Had to edit code file
MAX_MESSAGE_ID = 10  # Had to edit code file
```

### After (Configured in .env)
```python
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1003067861005'))  # Reads from .env
BOT_USERNAME = os.getenv('BOT_USERNAME', 'Test_videos69_bot')  # Reads from .env
MAX_MESSAGE_ID = int(os.getenv('MAX_MESSAGE_ID', '10'))  # Reads from .env
```

## Advantages

✅ **Easy to Change** - Just edit `.env` file, no code changes needed
✅ **Multiple Bots** - Different `.env` files for different bots
✅ **No Code Edits** - Keep `video69_bot.py` unchanged across bots
✅ **Secure** - `.env` is gitignored, keeps sensitive data private
✅ **Default Values** - Falls back to defaults if not set in `.env`

## Configuration Details

### CHANNEL_ID
- **Type:** Integer (negative number for private channels)
- **Example:** `-1003329285677`
- **How to get:** Use @userinfobot or @RawDataBot in your channel
- **Default:** `-1003067861005`

### BOT_USERNAME
- **Type:** String
- **Example:** `Test_videos69_bot`
- **Format:** Without the @ symbol
- **Used for:** Deep links and verification
- **Default:** `Test_videos69_bot`

### MAX_MESSAGE_ID
- **Type:** Integer
- **Example:** `2500`
- **Meaning:** The highest message ID in your channel
- **How to find:** Forward a recent message from your channel to @userinfobot
- **Default:** `10`

## How to Use for Different Bots

### Bot 1 (.env)
```env
CHANNEL_ID=-1003329285677
BOT_USERNAME=Videos1_69_bot
MAX_MESSAGE_ID=2500
```

### Bot 2 (.env)
```env
CHANNEL_ID=-1003456789012
BOT_USERNAME=Videos2_69_bot
MAX_MESSAGE_ID=5000
```

### Bot 3 (.env)
```env
CHANNEL_ID=-1003987654321
BOT_USERNAME=Videos3_69_bot
MAX_MESSAGE_ID=1000
```

**Same `video69_bot.py` file works for all bots!** Just change the `.env` file.

## Code Changes Made

### 1. video69_bot.py (Lines 24-77)

**Before:**
```python
CHANNEL_ID = -1003067861005  # Hardcoded
BOT_USERNAME = "Test_videos69_bot"  # Hardcoded
# MAX_MESSAGE_ID was inside get_random_video function
```

**After:**
```python
CHANNEL_ID = int(os.getenv('CHANNEL_ID', '-1003067861005'))  # From .env
BOT_USERNAME = os.getenv('BOT_USERNAME', 'Test_videos69_bot')  # From .env
MAX_MESSAGE_ID = int(os.getenv('MAX_MESSAGE_ID', '10'))  # From .env (global)
```

### 2. get_random_video Function (Lines 245-269)

**Before:**
```python
def get_random_video(user_id):
    # Configuration: message ID range in your channel
    MIN_MESSAGE_ID = 1
    MAX_MESSAGE_ID = 10  # Local variable
    ...
```

**After:**
```python
def get_random_video(user_id):
    # Use global configuration from .env file
    # MIN_MESSAGE_ID and MAX_MESSAGE_ID are defined at the top
    # Uses global MAX_MESSAGE_ID from .env
    ...
```

## Migration Steps

If you're updating an existing bot:

1. **Open your `.env` file**
2. **Add these three lines:**
   ```env
   CHANNEL_ID=-1003329285677
   BOT_USERNAME=Test_videos69_bot
   MAX_MESSAGE_ID=2500
   ```
3. **Update the values** to match your bot
4. **Save the file**
5. **Restart the bot** - Changes take effect immediately

## Finding Your Values

### CHANNEL_ID
1. Add @userinfobot to your channel
2. Forward any message from your channel to @userinfobot
3. Look for "Chat ID" - it will be a negative number like `-1003329285677`

### BOT_USERNAME
1. Open your bot in Telegram
2. Look at the username (e.g., @Test_videos69_bot)
3. Use just the username part: `Test_videos69_bot` (without @)

### MAX_MESSAGE_ID
1. Forward the most recent message from your channel to @userinfobot
2. Look for "Message ID" - use that number
3. Or add a buffer: if latest is 2450, use 2500

## Testing

After updating your `.env` file:

1. **Restart the bot**
2. **Check console output** - Should show your values
3. **Test video requests** - Should work with your channel
4. **Verify deep links** - Should use your bot username

## Troubleshooting

### Bot can't find channel
- ✅ Check CHANNEL_ID is correct (negative number)
- ✅ Ensure bot is admin in the channel
- ✅ Restart the bot after changing .env

### Videos not found
- ✅ Check MAX_MESSAGE_ID is high enough
- ✅ Ensure messages in that range are videos
- ✅ Bot needs access to channel

### Deep links not working
- ✅ Check BOT_USERNAME matches your actual bot username
- ✅ No @ symbol in BOT_USERNAME
- ✅ Restart bot after changes

## Summary

**What you need to do:**

1. ✅ Add 3 lines to your `.env` file
2. ✅ Update the values for your bot
3. ✅ Restart the bot
4. ✅ Done! No code changes needed

**Benefits:**
- 🚀 Quick setup for new bots
- 🔄 Easy to switch between bots
- 🔒 Secure configuration
- 📝 No code editing required

Now you can manage multiple bots easily by just changing the `.env` file!
