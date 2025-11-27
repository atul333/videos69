# Videos69 Telegram Bot

A Python-based Telegram bot that automatically collects and shares random videos from a Telegram channel.

## Features

- 🎬 Welcome message when users start the bot with `/start` command
- 🤖 Automatically collects videos from channel posts
- 📹 Random video selection without repetition
- ▶️ "Next" button to get another random video
- 🔄 Automatically resets when user has seen all videos
- 💾 Tracks which videos each user has seen

## Prerequisites

- Python 3.8 or higher
- A Telegram bot token
- Bot must be added as **admin** to the channel

## Setup

### 1. Add Bot as Admin to Channel

**Important:** The bot must be an admin in the `@movie_forward` channel to receive channel posts.

1. Go to your channel `@movie_forward`
2. Click on channel name → Administrators
3. Click "Add Administrator"
4. Search for `@Videos1_69_bot`
5. Add the bot as admin (it needs permission to see messages)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Bot

The `.env` file is already configured with your credentials:

```env
BOT_TOKEN=8568527168:AAFutr-YtLpKHk5MkoqD9URGHKOvtq1t4Ew
CHANNEL_USERNAME=movie_forward
```

### 4. Run the Bot

```bash
python bot.py
```

## How It Works

1. **Automatic Video Collection**: 
   - Bot is added as admin to the channel
   - When new videos are posted to the channel, the bot automatically receives them
   - Bot stores the message IDs of all video posts
   - Videos are collected in real-time as they're posted

2. **User Interaction**:
   - User sends `/start` command
   - Bot sends a welcome message with a "Get First Video" button
   - When user clicks the button, bot forwards a random video from the channel
   - Bot shows a "Next" button below the video
   - User can keep clicking "Next" to get more random videos

3. **Smart Video Selection**:
   - Bot tracks which videos each user has seen
   - Ensures users don't see the same video twice
   - When user has seen all videos, the history automatically resets

## Bot Commands

- `/start` - Start the bot and get welcome message

## Bot Information

- **Bot Username:** @Videos1_69_bot
- **Bot Link:** https://t.me/Videos1_69_bot
- **Source Channel:** @movie_forward (https://t.me/movie_forward)

## Technical Details

### Libraries Used

- **python-telegram-bot**: For bot functionality and user interaction
- **python-dotenv**: For managing environment variables

### How Video Collection Works

The bot uses the Telegram Bot API's `channel_post` update type to automatically receive new posts from the channel. When the bot is an admin:
- It receives all new posts in real-time
- Automatically filters and stores video posts
- No need for manual video ID entry
- Works seamlessly with the Bot API

## Troubleshooting

### Bot not starting
- Make sure you've installed all dependencies: `pip install -r requirements.txt`
- Verify your bot token in `.env` file

### No videos loading
- **Make sure the bot is added as admin to the channel** (most common issue)
- Check that the channel username is correct in `.env`
- Videos will only be collected from NEW posts after the bot starts
- Post a test video to the channel to verify collection is working

### "No videos available" message
- The bot collects videos in real-time from channel posts
- If you just started the bot, there are no videos yet
- Post a new video to the channel, and it will be automatically collected
- The bot will show: `📹 New video added! Message ID: XXX | Total videos: 1`

### Videos not forwarding
- Ensure the channel allows message forwarding
- Check that the bot has admin permissions in the channel

## Important Notes

⚠️ **Video Collection**: This bot collects videos from NEW channel posts after it starts running. It does not fetch historical videos. To build your video library:
- Keep the bot running
- Post videos to the channel
- Bot will automatically collect them

💡 **Tip**: If you need to collect existing videos from the channel, you would need to either:
- Repost them to the channel (while bot is running)
- Or manually add message IDs to the code

## Security Notes

- Keep your `.env` file secure and never share it publicly
- The bot token can control your bot, keep it private
- Only trusted admins should have access to the channel

## File Structure

```
Videos69 bot/
├── bot.py              # Main bot script
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (bot token)
└── README.md          # This file
```

## License

ISC

