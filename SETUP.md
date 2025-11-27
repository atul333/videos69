# Quick Setup Guide

## Step 1: Add Bot as Admin to Channel

**IMPORTANT:** The bot must be an admin in the channel!

1. Open Telegram and go to @movie_forward channel
2. Click on channel name → Administrators
3. Click "Add Administrator"
4. Search for @Videos1_69_bot
5. Add the bot as admin with permissions to:
   - Post messages (needed for testing)

## Step 2: Install Dependencies

Open terminal in this folder and run:
```bash
pip install -r requirements.txt
```

## Step 3: Run the Bot

```bash
python bot.py
```

**Note:** The bot starts **instantly**! No video loading needed.

## Step 4: Test the Bot

1. Open Telegram and search for @Videos1_69_bot
2. Click "Start" or type /start
3. Click "Get First Video" button
4. Click "Next" button to get more videos

## How It Works

✅ Bot generates random message IDs from the channel (1-3000)
✅ Tries to send random messages - if it's a video, success!
✅ If not a video or doesn't exist, tries another random ID
✅ Shows welcome message when user types /start
✅ Sends random videos to users from the channel
✅ Provides "Next" button to get more videos
✅ Tracks which message IDs each user has seen
✅ Never shows the same message twice (until all are seen)
✅ Videos auto-delete after 10 minutes
✅ **Instant startup - no loading time!**

## Important Notes

✅ The bot uses random message IDs - no pre-loading needed!
✅ Bot starts instantly - ready to use immediately
✅ Automatically skips non-video messages
✅ Adjust MAX_MESSAGE_ID in bot.py based on your channel size
⚠️ Make sure the bot is an admin in the channel

Enjoy! 🎬

