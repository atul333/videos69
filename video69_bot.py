import os
import random
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.request import HTTPXRequest
import aiohttp
import hashlib

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_USERNAME = os.getenv('CHANNEL_USERNAME')
CHANNEL_ID = -1003389539131  # Private channel ID

# Use channel ID for private channels, username for public channels
CHANNEL_IDENTIFIER = CHANNEL_ID if CHANNEL_ID else f"@{CHANNEL_USERNAME}"

# Admin configuration for support system
ADMIN_USER_ID = 7708376300  # Admin's Telegram user ID (https://t.me/Deep12048)

# Configure request with longer timeouts
request = HTTPXRequest(
    connection_pool_size=8,
    connect_timeout=30.0,  # 30 seconds for connection
    read_timeout=30.0,     # 30 seconds for reading
    write_timeout=30.0,    # 30 seconds for writing
    pool_timeout=30.0      # 30 seconds for pool
)

# Store video message IDs
video_messages = []
# Store user states to track which videos they've seen, daily limits, and premium access
# Structure: {user_id: {'seen_videos': [], 'daily_count': 0, 'last_reset': datetime, 'premium_until': datetime}}
user_states = {}
# Track used tokens to prevent link reuse
used_tokens = set()
# Track all users who have started the bot (for broadcasting)
all_users = set()

# Hourly video limit for free users (resets every hour)
HOURLY_VIDEO_LIMIT = 10
# Premium access duration after watching ad (12 hours)
PREMIUM_DURATION_HOURS = 12

# VPLink API Configuration
VPLINK_API_TOKEN = "602a4c7facf8ec279b28f8763cd0f5e246252d59"
VPLINK_API_URL = "https://vplink.in/api"
# Bot username for deep links
BOT_USERNAME = "Videos1_69_bot"
# Secret key for encrypting verification tokens
SECRET_KEY = "your_secret_key_here_change_this"  # Change this to a random secret

# Mandatory channel to join (forced subscription)
# For private channels, you need to use the numeric chat ID (get it from @userinfobot)
# For public channels, use @channelname
MANDATORY_CHANNEL = -1003363678621  # Replace with your channel's numeric ID
MANDATORY_CHANNEL_LINK = "https://t.me/+Pkij1IcrzhJjMDBl"

# User data file path
USERS_FILE = "users.json"

# Cache for user data (loaded once, updated in memory)
_users_cache = None
_cache_loaded = False


# User file management functions (optimized for unlimited users)
def load_users_from_file():
    """Load users from JSON file (with caching)"""
    global _users_cache, _cache_loaded
    
    # Return cached data if already loaded
    if _cache_loaded and _users_cache is not None:
        return _users_cache
    
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                _users_cache = json.load(f)
                _cache_loaded = True
                print(f"📂 Loaded {len(_users_cache)} users from file")
                return _users_cache
        else:
            print("📂 No users file found, starting fresh")
            _users_cache = []
            _cache_loaded = True
            return []
    except Exception as e:
        print(f"⚠️ Error loading users file: {e}")
        _users_cache = []
        _cache_loaded = True
        return []


def save_users_to_file(users_data):
    """Save users to JSON file (optimized write)"""
    global _users_cache
    try:
        # Update cache
        _users_cache = users_data
        
        # Write to file (async-safe)
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=2, ensure_ascii=False)
        
        # Don't print on every save to reduce console spam
        # print(f"💾 Saved {len(users_data)} users to file")
    except Exception as e:
        print(f"⚠️ Error saving users file: {e}")


def add_user_to_file(user_id, first_name, username=None):
    """Add a new user to the file (checks for duplicates) - optimized"""
    users_data = load_users_from_file()
    
    # Use dictionary for O(1) lookup instead of O(n) list iteration
    user_dict = {user['user_id']: user for user in users_data}
    
    # Check if user already exists
    if user_id in user_dict:
        # User exists, update name if changed
        user = user_dict[user_id]
        if user['first_name'] != first_name or user.get('username') != username:
            user['first_name'] = first_name
            user['username'] = username
            user['last_seen'] = datetime.now(timezone.utc).isoformat()
            save_users_to_file(users_data)
            # print(f"🔄 Updated user: {first_name} (ID: {user_id})")
        return False  # User already existed
    
    # Add new user
    new_user = {
        'user_id': user_id,
        'first_name': first_name,
        'username': username,
        'joined_date': datetime.now(timezone.utc).isoformat(),
        'last_seen': datetime.now(timezone.utc).isoformat()
    }
    users_data.append(new_user)
    save_users_to_file(users_data)
    print(f"✅ Added new user: {first_name} (ID: {user_id})")
    return True  # New user added


def get_all_user_ids():
    """Get list of all user IDs from file (cached, very fast)"""
    users_data = load_users_from_file()
    return [user['user_id'] for user in users_data]


def get_user_count():
    """Get total number of users (O(1) operation)"""
    users_data = load_users_from_file()
    return len(users_data)


def batch_remove_users(user_ids_to_remove):
    """Remove multiple users at once (optimized for broadcast cleanup)"""
    if not user_ids_to_remove:
        return
    
    users_data = load_users_from_file()
    remove_set = set(user_ids_to_remove)
    
    # Filter out users to remove (single pass)
    users_data = [u for u in users_data if u['user_id'] not in remove_set]
    
    save_users_to_file(users_data)
    print(f"🗑️ Removed {len(user_ids_to_remove)} users from file")


async def check_channel_membership(context: ContextTypes.DEFAULT_TYPE, user_id: int) -> bool:
    """Check if user is a member of the mandatory channel"""
    try:
        # Get user's status in the channel
        member = await context.bot.get_chat_member(chat_id=MANDATORY_CHANNEL, user_id=user_id)
        
        # Check if user is a member (member, administrator, or creator)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        else:
            return False
    except Exception as e:
        print(f"⚠️ Error checking channel membership for user {user_id}: {e}")
        return False


def get_main_menu_keyboard():
    """Create the persistent menu keyboard with main buttons"""
    keyboard = [
        [KeyboardButton("🎬 Get New Video"), KeyboardButton("💬 Contact Us")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def load_videos_from_channel(application: Application):
    """Initialize bot - no video loading needed!"""
    
    try:
        print(f"📡 Connecting to channel...")
        
        # Get channel chat
        chat = await application.bot.get_chat(CHANNEL_IDENTIFIER)
        print(f"✅ Connected to channel: {chat.title}")
        print(f"📋 Channel ID: {chat.id}")
        
        print("\n✅ Bot ready! Videos will be sent randomly from the channel.")
        print("💡 No pre-loading needed - instant startup!\n")
        
        # We don't load videos anymore - we'll generate random message IDs
        # and try to send them. If they don't exist or aren't videos, we'll try another.
        
    except Exception as e:
        print(f"❌ Error connecting to channel: {e}")
        print("⚠️ Make sure the bot is an admin in the channel.")



# Channel post handler removed - bot only uses predefined videos


def get_random_video(user_id):
    """Generate a random video message ID that the user hasn't seen yet"""
    
    if user_id not in user_states:
        init_user_state(user_id)
    
    user_state = user_states[user_id]
    
    # Configuration: message ID range in your channel
    MIN_MESSAGE_ID = 1
    MAX_MESSAGE_ID = 20000  # Adjust based on your channel size
    
    # Generate a list of all possible message IDs
    all_message_ids = list(range(MIN_MESSAGE_ID, MAX_MESSAGE_ID + 1))
    
    # Filter out videos the user has already seen
    unseen_ids = [mid for mid in all_message_ids if mid not in user_state['seen_videos']]
    
    # If user has seen all videos, reset their history
    if not unseen_ids:
        user_state['seen_videos'] = []
        unseen_ids = all_message_ids
    
    # Return a random unseen message ID
    return random.choice(unseen_ids)



def mark_video_as_seen(user_id, video_id):
    """Mark a video as seen by the user"""
    if user_id not in user_states:
        init_user_state(user_id)
    
    if video_id not in user_states[user_id]['seen_videos']:
        user_states[user_id]['seen_videos'].append(video_id)


def init_user_state(user_id):
    """Initialize user state with default values"""
    if user_id not in user_states:
        now = datetime.now(timezone.utc)
        # Set last_reset to the start of the current hour
        last_reset = now.replace(minute=0, second=0, microsecond=0)
        user_states[user_id] = {
            'seen_videos': [],
            'hourly_count': 0,
            'last_reset': last_reset,
            'premium_until': None,
            'ad_link': None,  # Store the unique ad link for this user
            'ad_token': None  # Store the verification token
        }


def is_premium_user(user_id):
    """Check if user has active premium access"""
    if user_id not in user_states:
        init_user_state(user_id)
    
    premium_until = user_states[user_id].get('premium_until')
    if premium_until and datetime.now(timezone.utc) < premium_until:
        return True
    return False


def check_and_reset_hourly_limit(user_id):
    """Check if hourly limit needs to be reset (at the start of each hour)"""
    if user_id not in user_states:
        init_user_state(user_id)
    
    user_state = user_states[user_id]
    now = datetime.now(timezone.utc)
    
    # Get the start of the current hour
    current_hour_start = now.replace(minute=0, second=0, microsecond=0)
    
    # Reset if we've moved to a new hour
    if current_hour_start > user_state['last_reset']:
        user_state['hourly_count'] = 0
        user_state['last_reset'] = current_hour_start
        return True  # Indicate that reset occurred
    return False  # No reset occurred


def can_watch_video(user_id):
    """Check if user can watch a video (premium or within hourly limit)"""
    if is_premium_user(user_id):
        return True
    
    check_and_reset_hourly_limit(user_id)
    return user_states[user_id]['hourly_count'] < HOURLY_VIDEO_LIMIT


def increment_video_count(user_id):
    """Increment user's hourly video count"""
    if user_id not in user_states:
        init_user_state(user_id)
    
    user_states[user_id]['hourly_count'] += 1


def utc_to_ist(utc_time):
    """Convert UTC datetime to IST (UTC+5:30)"""
    ist_offset = timedelta(hours=5, minutes=30)
    return utc_time + ist_offset


def grant_premium_access(user_id):
    """Grant premium access for 12 hours after watching ad"""
    if user_id not in user_states:
        init_user_state(user_id)
    
    user_states[user_id]['premium_until'] = datetime.now(timezone.utc) + timedelta(hours=PREMIUM_DURATION_HOURS)


async def create_shortened_link(user_id):
    """Create a unique shortened link that opens the bot with encrypted token"""
    if user_id not in user_states:
        init_user_state(user_id)
    
    # Generate a unique verification token
    timestamp = int(datetime.now().timestamp())
    random_part = random.randint(10000, 99999)
    
    # Create token: user_id + timestamp + random
    token_data = f"{user_id}_{timestamp}_{random_part}"
    
    # Encrypt the token using SHA256
    encrypted_token = hashlib.sha256(f"{token_data}_{SECRET_KEY}".encode()).hexdigest()[:16]
    
    # Create the full token (we'll verify this later)
    full_token = f"{user_id}_{timestamp}_{encrypted_token}"
    
    # Store the token in user state for verification
    user_states[user_id]['ad_token'] = full_token
    
    # Create Telegram bot deep link
    # Format: https://t.me/BotUsername?start=token
    bot_deep_link = f"https://t.me/{BOT_USERNAME}?start={full_token}"
    
    # Generate unique alias for VPLink
    alias = f"v_{user_id}_{timestamp}"
    
    # Build VPLink API URL to shorten the bot deep link
    api_url = f"{VPLINK_API_URL}?api={VPLINK_API_TOKEN}&url={bot_deep_link}&alias={alias}&format=text"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    shortened_url = await response.text()
                    shortened_url = shortened_url.strip()
                    
                    # Store the shortened link in user state
                    user_states[user_id]['ad_link'] = shortened_url
                    
                    print(f"✅ Created shortened link for user {user_id}: {shortened_url}")
                    print(f"   Token: {full_token}")
                    return shortened_url
                else:
                    print(f"❌ Failed to create shortened link: {response.status}")
                    return None
    except Exception as e:
        print(f"❌ Error creating shortened link: {e}")
        return None



def validate_ad_link(user_id, clicked_link):
    """Validate if the clicked link matches the user's assigned link"""
    if user_id not in user_states:
        return False
    
    stored_link = user_states[user_id].get('ad_link')
    if stored_link and stored_link == clicked_link:
        return True
    return False

async def delete_messages(context: ContextTypes.DEFAULT_TYPE):
    """Delete messages after 10 minutes"""
    job_data = context.job.data
    chat_id = job_data['chat_id']
    message_ids = job_data['message_ids']
    
    # Delete the video and warning messages
    for message_id in message_ids:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
        except Exception as e:
            print(f"⚠️ Could not delete message {message_id}: {e}")
    
    print(f"🗑️ Deleted {len(message_ids)} messages in chat {chat_id}")
    
    # No notification message - keep the chat clean!


async def broadcast_hourly_reset(context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message to all users about hourly limit reset - sent every hour"""
    
    print("\n" + "=" * 60)
    print("🔔 HOURLY BROADCAST TRIGGERED!")
    print("=" * 60)
    
    # Get current time in IST
    from datetime import datetime, timedelta, timezone
    ist_offset = timedelta(hours=5, minutes=30)
    current_time_ist = datetime.now(timezone.utc) + ist_offset
    time_str = current_time_ist.strftime('%I:00 %p')  # e.g., "01:00 PM"
    date_str = current_time_ist.strftime('%B %d, %Y')  # e.g., "November 30, 2025"
    
    print(f"⏰ Broadcasting at: {time_str} IST")
    print(f"📅 Date: {date_str}")
    
    # Create "Watch Now" button
    keyboard = [[InlineKeyboardButton("🎬 Watch Now", callback_data='next_video')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        f"🎬 **Hourly Limit Reset!** 🎬\n\n"
        f"⏰ Time: **{time_str} IST**\n"
        f"📅 Date: **{date_str}**\n\n"
        f"✨ Your hourly limit has been renewed!\n"
        f"🎥 You can now watch **10 free videos**\n\n"
        f"💎 No ads required - just start watching!\n\n"
        f"Click below to start watching!\n\n"
        f"Enjoy! 🍿"
    )
    
    # Load user IDs from file (persistent storage)
    user_ids = get_all_user_ids()
    
    # Send to all users
    successful = 0
    failed = 0
    blocked_users = []
    
    for user_id in user_ids:
        try:
            await context.bot.send_message(
                chat_id=user_id,
                text=message_text,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            successful += 1
            
            # Add small delay to avoid hitting rate limits
            import asyncio
            await asyncio.sleep(0.05)  # 50ms delay between messages
            
        except Exception as e:
            failed += 1
            # User might have blocked the bot or deleted their account
            print(f"⚠️ Could not send broadcast to user {user_id}: {e}")
            
            # Track blocked users to remove from file
            if "Forbidden" in str(e) or "blocked" in str(e).lower():
                blocked_users.append(user_id)
                # Also remove from in-memory set
                all_users.discard(user_id)
    
    # Remove blocked users from file (batch operation - very efficient)
    if blocked_users:
        batch_remove_users(blocked_users)
    
    print(f"📢 Hourly broadcast complete! Sent to {successful} users, {failed} failed")
    print(f"⏰ Broadcast time: {time_str} IST")
    print(f"📅 Broadcast date: {date_str}")
    print(f"👥 Total users in database: {get_user_count()}")




async def send_random_video(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id=None, user_id=None):
    """Send a random video to the user"""
    if chat_id is None:
        chat_id = update.effective_chat.id
    if user_id is None:
        user_id = update.effective_user.id
    
    try:
        # FIRST: Check if user is still a member of the mandatory channel
        is_member = await check_channel_membership(context, user_id)
        
        if not is_member:
            # User hasn't joined or left the channel - show join message
            keyboard = [
                [InlineKeyboardButton("📢 Join Channel", url=MANDATORY_CHANNEL_LINK)],
                [InlineKeyboardButton("🔄 Refresh", callback_data='check_membership')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=chat_id,
                text="🔒 **Channel Membership Required!**\n\n"
                     "You must join our channel to use this bot.\n\n"
                     "📢 **Steps**:\n"
                     "1. Click 'Join Channel' button below\n"
                     "2. Join the channel\n"
                     "3. Click 'Refresh' button to verify\n\n"
                     "After joining, you can watch videos! 🎬",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return  # Stop here - don't send video
        
        # Check if user can watch videos (daily limit or premium)
        if not can_watch_video(user_id):
            # Check if user had premium that expired
            if user_id in user_states and user_states[user_id].get('premium_until'):
                premium_until = user_states[user_id]['premium_until']
                if datetime.now(timezone.utc) >= premium_until:
                    # Premium has expired - calculate next hourly reset
                    now = datetime.now(timezone.utc)
                    next_reset = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
                    next_reset_ist = utc_to_ist(next_reset)
                    time_until_reset = next_reset - now
                    minutes_until_reset = int(time_until_reset.total_seconds() / 60)
                    
                    keyboard = [[InlineKeyboardButton("📺 Watch Ad", callback_data='watch_ad')]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"⏰ **Premium Access Expired!**\n\n"
                             f"Your premium access has ended.\n\n"
                             f"**Options**:\n"
                             f"• 📺 Watch an ad to get 12 more hours of premium\n"
                             f"• ⏰ Wait {minutes_until_reset} minutes for your hourly limit to reset at {next_reset_ist.strftime('%I:%M %p')} IST\n\n"
                             f"Choose an option below:",
                        parse_mode='Markdown',
                        reply_markup=reply_markup
                    )
                    return
            
            # Regular hourly limit reached (no premium or never had premium)
            # Calculate next reset time
            now = datetime.now(timezone.utc)
            next_reset = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
            next_reset_ist = utc_to_ist(next_reset)
            time_until_reset = next_reset - now
            minutes_until_reset = int(time_until_reset.total_seconds() / 60)
            
            keyboard = [[InlineKeyboardButton("📺 Watch Ad", callback_data='watch_ad')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ **Hourly Limit Reached!**\n\n"
                     f"You've watched all 10 videos for this hour.\n\n"
                     f"**Options**:\n"
                     f"• 📺 Watch an ad to get 12 hours of unlimited access\n"
                     f"• ⏰ Wait {minutes_until_reset} minutes for your hourly limit to reset at {next_reset_ist.strftime('%I:%M %p')} IST\n\n"
                     f"Choose an option below:",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            return
        
        # Try to find a valid video (try up to 10 random message IDs)
        max_attempts = 10
        video_sent = False
        
        for attempt in range(max_attempts):
            try:
                # Get a random message ID
                message_id = get_random_video(user_id)
                
                # Try to copy the message from the channel
                video_msg = await context.bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=CHANNEL_IDENTIFIER,
                    message_id=message_id,
                    protect_content=True  # Disable forward/copy/save options
                )
                
                # If we got here, the message was sent successfully
                # Mark video as seen
                mark_video_as_seen(user_id, message_id)
                
                # Increment daily video count (for non-premium users)
                if not is_premium_user(user_id):
                    increment_video_count(user_id)
                
                # Create "Next" button with deletion warning
                keyboard = [[InlineKeyboardButton("▶️ Next", callback_data='next_video')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                # Send "Next" button with deletion warning
                warning_msg = await context.bot.send_message(
                    chat_id=chat_id,
                    text="👆 Enjoy the video!\n\n⚠️ This video will be deleted after 10 minutes.",
                    reply_markup=reply_markup
                )
                
                # Schedule deletion of both video and warning message after 10 minutes (600 seconds)
                context.job_queue.run_once(
                    delete_messages,
                    when=600,  # 10 minutes in seconds
                    data={'chat_id': chat_id, 'message_ids': [video_msg.message_id, warning_msg.message_id]},
                    name=f"delete_{chat_id}_{video_msg.message_id}"
                )
                
                video_sent = True
                print(f"✅ Sent video message ID {message_id} to user {user_id}")
                break  # Success! Exit the loop
                
            except Exception as e:
                # This message ID doesn't exist or isn't a video, try another
                print(f"⚠️ Message ID {message_id} failed: {e}")
                # Mark as seen so we don't try it again
                mark_video_as_seen(user_id, message_id)
                continue
        
        # If we couldn't find any valid video after all attempts
        if not video_sent:
            keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data='next_video')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=chat_id,
                text="⚠️ No videos available at the moment.\n\nPlease try again!",
                reply_markup=reply_markup
            )
        
    except Exception as e:
        print(f"❌ Error sending video: {e}")
        keyboard = [[InlineKeyboardButton("🔄 Try Again", callback_data='next_video')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ Sorry, there was an error sending the video. Please try again.",
            reply_markup=reply_markup
        )


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_id = user.id
    first_name = user.first_name or "there"
    username = user.username
    
    # Track this user for broadcasting (in-memory)
    all_users.add(user_id)
    
    # Save user to file (persistent storage)
    add_user_to_file(user_id, first_name, username)
    
    # Check if user is a member of the mandatory channel
    is_member = await check_channel_membership(context, user_id)
    
    if not is_member:
        # User hasn't joined the channel - show join message
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=MANDATORY_CHANNEL_LINK)],
            [InlineKeyboardButton("🔄 Refresh", callback_data='check_membership')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"👋 Welcome {first_name}!\n\n"
            f"🔒 To use this bot, you must join our channel first.\n\n"
            f"📢 **Steps**:\n"
            f"1. Click 'Join Channel' button below\n"
            f"2. Join the channel\n"
            f"3. Click 'Refresh' button to verify\n\n"
            f"After joining, you'll get full access to the bot! 🎬",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        return  # Stop here until user joins
    
    # Check if user came from ad link (deep link with token)
    if context.args and len(context.args) > 0:
        token = context.args[0]
        
        # Verify the token belongs to this user and hasn't been used
        if token in used_tokens:
            # Token already used
            await update.message.reply_text(
                "❌ This link has already been used!\n\n"
                "Each ad link can only be used once. Please watch a new ad to get premium access.",
            )
            print(f"⚠️ User {user_id} tried to reuse token: {token}")
            return
        
        # Validate token format: user_id_timestamp_hash
        try:
            token_parts = token.split('_')
            if len(token_parts) >= 3:
                token_user_id = int(token_parts[0])
                
                # Check if token belongs to this user
                if token_user_id == user_id:
                    # Check if this is the user's assigned token
                    if user_id in user_states and user_states[user_id].get('ad_token') == token:
                        # Valid token! Grant premium access
                        grant_premium_access(user_id)
                        used_tokens.add(token)  # Mark token as used
                        
                        # Clear the stored token
                        user_states[user_id]['ad_token'] = None
                        user_states[user_id]['ad_link'] = None
                        
                        # Calculate expiry time in IST
                        expiry_time_utc = user_states[user_id]['premium_until']
                        expiry_time_local = utc_to_ist(expiry_time_utc)
                        
                        # Send premium activation message
                        keyboard = [[InlineKeyboardButton("🎬 Get Video", callback_data='next_video')]]
                        reply_markup = InlineKeyboardMarkup(keyboard)
                        
                        await update.message.reply_text(
                            f"✅ **Premium Access Activated!**\n\n"
                            f"Hello {first_name}! 👋\n\n"
                            f"🎉 You now have **unlimited access** for the next **12 hours**!\n\n"
                            f"⏰ Your premium access will expire at: {expiry_time_local.strftime('%I:%M %p')} IST\n\n"
                            f"🎥 Click below to start watching unlimited videos!\n\n"
                            f"Enjoy! 🍿",
                            parse_mode='Markdown',
                            reply_markup=reply_markup
                        )
                        
                        print(f"✅ Premium activated for user: {first_name} (ID: {user_id})")
                        return
                    else:
                        await update.message.reply_text(
                            "❌ Invalid or expired ad link!\n\n"
                            "Please watch a new ad to get premium access."
                        )
                        print(f"⚠️ Invalid token for user {user_id}: {token}")
                        return
                else:
                    await update.message.reply_text(
                        "❌ This link was created for a different user!\n\n"
                        "Please watch the ad yourself to get premium access."
                    )
                    print(f"⚠️ User {user_id} tried to use token for user {token_user_id}")
                    return
        except Exception as e:
            print(f"⚠️ Error validating token: {e}")
            # Continue to show welcome message if token is invalid
    
    # Check if user already has premium
    if is_premium_user(user_id):
        premium_until = user_states[user_id]['premium_until']
        time_remaining = premium_until - datetime.now(timezone.utc)
        hours_remaining = int(time_remaining.total_seconds() / 3600)
        minutes_remaining = int((time_remaining.total_seconds() % 3600) / 60)
        
        # Convert expiry time to IST
        expiry_time_local = utc_to_ist(premium_until)
        
        keyboard = [[InlineKeyboardButton("🎬 Get Video", callback_data='next_video')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"🎬 **Welcome Back, {first_name}!** 🎬\n\n"
            f"✅ You have **Premium Access**!\n\n"
            f"⏰ Time remaining: **{hours_remaining}h {minutes_remaining}m**\n"
            f"⏰ Expires at: **{expiry_time_local.strftime('%I:%M %p')} IST**\n\n"
            f"🎥 Click below to watch unlimited videos!\n\n"
            f"Enjoy! 🍿",
            parse_mode='Markdown',
            reply_markup=reply_markup
        )
        print(f"✅ Premium user returned: {first_name} (ID: {user_id})")
        return
    
    # Regular welcome message for new/non-premium users
    welcome_message = f"""
🎬 **Welcome to Videos Bot!** 🎬

Hello {first_name}! 👋

I'm here to share amazing videos with you from our collection.

🎥 You can watch **10 videos per hour** for free!
⏰ Your limit resets every hour (1:00 PM, 2:00 PM, etc.)

💎 Want unlimited access? Watch an ad to get **12 hours of premium**!

Enjoy! 🍿
    """
    
    # Create \"Get First Video\" inline button
    inline_keyboard = [[InlineKeyboardButton("🎬 Get First Video", callback_data='next_video')]]
    inline_markup = InlineKeyboardMarkup(inline_keyboard)
    
    # Get persistent menu keyboard
    menu_keyboard = get_main_menu_keyboard()
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown',
        reply_markup=menu_keyboard  # Show persistent menu
    )
    
    # Send inline button separately
    await update.message.reply_text(
        "👇 Click below to get your first video:",
        reply_markup=inline_markup
    )
    
    print(f"✅ New user started the bot: {first_name} (ID: {user_id})")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - Direct users to admin bot"""
    user = update.effective_user
    first_name = user.first_name or "there"
    
    help_message = f"""
❓ **Need Help?** ❓

Hello {first_name}! 👋

If you're facing any issues or have questions, you can contact our admin!

📞 **Contact Admin Bot:**
Click the button below to message our admin support bot.

👨‍💼 **Admin Support Available**

Your message will be forwarded to the admin, and they will reply to you directly!
    """
    
    # Create button to admin bot
    keyboard = [[InlineKeyboardButton("💬 Contact Admin", url="https://t.me/videos69Admin_Bot")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        help_message,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )
    print(f"📞 User {user.id} requested help - directed to admin bot")


async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular messages - Forward to/from admin OR handle menu buttons"""
    # Ignore messages without a user (e.g., channel posts)
    if not update.effective_user:
        return
    
    user_id = update.effective_user.id
    message = update.message
    
    # Check if it's a menu button press
    if message.text:
        if message.text == "🎬 Get New Video":
            # User clicked "Get New Video" button
            await send_random_video(
                update,
                context,
                chat_id=message.chat_id,
                user_id=user_id
            )
            return
        
        elif message.text == "💬 Contact Us":
            # User clicked "Contact Us" button - show admin bot link
            first_name = update.effective_user.first_name or "there"
            
            help_message = f"""
❓ **Need Help?** ❓

Hello {first_name}! 👋

If you're facing any issues or have questions, you can contact our admin!

📞 **Contact Admin Bot:**
Click the button below to message our admin support bot.

👨‍💼 **Admin Support Available**

Your message will be forwarded to the admin, and they will reply to you directly!
            """
            
            # Create button to admin bot
            keyboard = [[InlineKeyboardButton("💬 Contact Admin", url="https://t.me/videos69Admin_Bot")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await message.reply_text(
                help_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            print(f"📞 User {user_id} requested help via menu button")
            return
    
    # If not a menu button, ignore other text messages (no forwarding to admin from main bot)
    # Admin communication happens through the separate admin bot


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    
    # Try to answer the query, but ignore timeout errors
    try:
        await query.answer()
    except Exception as e:
        # Ignore "Query is too old" errors
        print(f"⚠️ Could not answer callback query: {e}")
    
    if query.data == 'check_membership':
        # User clicked refresh button - check if they joined the channel
        user_id = query.from_user.id
        first_name = query.from_user.first_name or "there"
        
        is_member = await check_channel_membership(context, user_id)
        
        if is_member:
            # User has joined! Show welcome message
            keyboard = [[InlineKeyboardButton("🎬 Get First Video", callback_data='next_video')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.message.edit_text(
                    f"✅ **Verified!**\n\n"
                    f"Welcome {first_name}! 👋\n\n"
                    f"You've successfully joined the channel!\n\n"
                    f"🎥 You can watch **10 videos per hour** for free!\n"
                    f"⏰ Your limit resets every hour!\n\n"
                    f"💎 Want unlimited access? Watch an ad to get **12 hours of premium**!\n\n"
                    f"Click below to start watching! 🍿",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                # Ignore "Message is not modified" errors
                if "Message is not modified" not in str(e):
                    print(f"⚠️ Error editing message: {e}")
        else:
            # User still hasn't joined
            keyboard = [
                [InlineKeyboardButton("📢 Join Channel", url=MANDATORY_CHANNEL_LINK)],
                [InlineKeyboardButton("🔄 Refresh", callback_data='check_membership')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            try:
                await query.message.edit_text(
                    f"❌ **Not Joined Yet**\n\n"
                    f"You haven't joined the channel yet.\n\n"
                    f"📢 **Please**:\n"
                    f"1. Click 'Join Channel' button\n"
                    f"2. Join the channel\n"
                    f"3. Click 'Refresh' again\n\n"
                    f"You must join to use this bot! 🔒",
                    parse_mode='Markdown',
                    reply_markup=reply_markup
                )
            except Exception as e:
                # Ignore "Message is not modified" errors
                if "Message is not modified" not in str(e):
                    print(f"⚠️ Error editing message: {e}")
    
    elif query.data == 'next_video':
        await send_random_video(
            update,
            context,
            chat_id=query.message.chat_id,
            user_id=query.from_user.id
        )
    
    elif query.data == 'watch_ad':
        # Create a unique shortened link for this user
        user_id = query.from_user.id
        shortened_link = await create_shortened_link(user_id)
        
        if shortened_link:
            # Show ad watching instructions with the shortened link
            keyboard = [
                [InlineKeyboardButton("📺 Click Here to Watch Ad", url=shortened_link)],
                [InlineKeyboardButton("❓ How to Open Link", callback_data='how_to_open')]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="📺 **Watch Ad to Get Premium Access**\n\n"
                     "🎯 **Instructions**:\n"
                     "1. Click the 'Click Here to Watch Ad' button below\n"
                     "2. Complete the ad verification process\n"
                     "3. You'll be automatically redirected back to the bot\n"
                     "4. **Premium will activate automatically!**\n\n"
                     "⚠️ **iOS Users**: Copy the link and open it in Chrome browser\n\n"
                     "💎 You'll get **12 hours of unlimited video access**!",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
        else:
            # Error creating link
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="❌ Error creating ad link. Please try again later."
            )
    
    elif query.data == 'how_to_open':
        # Show instructions on how to open the link
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text="❓ **How to Open the Ad Link**:\n\n"
                 "**For iOS Users**:\n"
                 "1. Click on the 'Click Here to Watch Ad' button\n"
                 "2. Copy the link that appears\n"
                 "3. Open Chrome browser on your device\n"
                 "4. Paste and open the link\n"
                 "5. Complete the ad viewing process\n"
                 "6. You'll be redirected back automatically!\n\n"
                 "**For Android Users**:\n"
                 "1. Simply click the 'Click Here to Watch Ad' button\n"
                 "2. Complete the ad verification\n"
                 "3. You'll be redirected back automatically!\n\n"
                 "✅ Premium will activate automatically when you return!",
            parse_mode='Markdown'
        )



async def post_init(application: Application):
    """Initialize bot after startup"""
    await load_videos_from_channel(application)


def main():
    """Start the bot"""
    print("🤖 Starting Videos Bot System...")
    print("=" * 50)
    
    # Start the admin bot in a separate process (Windows only)
    # On Linux, use start_bots.sh script instead
    admin_bot_process = None
    if sys.platform == "win32":
        try:
            print("📱 [1/2] Starting Admin Support Bot...")
            admin_bot_path = os.path.join(os.path.dirname(__file__), "admin_bot.py")
            
            admin_bot_process = subprocess.Popen(
                [sys.executable, admin_bot_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
            
            print("✅ Admin Bot started successfully!")
            print(f"   Bot: @videos69Admin_Bot")
            print(f"   Admin: ")
            print()
        except Exception as e:
            print(f"⚠️ Warning: Could not start admin bot: {e}")
            print("   You can start it manually: python admin_bot.py")
            print()
    else:
        print("ℹ️ On Linux, use './start_bots.sh' to start both bots")
        print()
    
    print("🎬 [2/2] Starting Main Videos Bot...")
    print("🌐 Connecting to Telegram API...")
    print()
    
    try:
        # Create the Application with custom request settings
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .request(request)  # Use custom request with longer timeouts
            .post_init(post_init)
            .build()
        )
        
        # Add command handlers
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        
        # Add callback query handler for buttons
        application.add_handler(CallbackQueryHandler(button_callback))
        
        # Add message handler for persistent menu buttons
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
        
        # Channel post handler disabled - using random message IDs
        
        # Schedule hourly broadcast at the start of each hour (when hourly limit resets)
        from datetime import time
        import pytz
        
        # IST timezone
        ist_tz = pytz.timezone('Asia/Kolkata')
        
        # Calculate when to run the first broadcast (at the next hour mark)
        now_utc = datetime.now(timezone.utc)
        now_ist = now_utc + timedelta(hours=5, minutes=30)
        
        # Calculate next hour (e.g., if it's 12:37, next hour is 13:00)
        next_hour_ist = (now_ist + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        next_hour_utc = next_hour_ist - timedelta(hours=5, minutes=30)
        
        # Calculate seconds until next hour
        seconds_until_next_hour = (next_hour_utc - now_utc).total_seconds()
        
        # Schedule for every hour at :00 minutes
        job_queue = application.job_queue
        
        # Run at the top of every hour
        job_queue.run_repeating(
            broadcast_hourly_reset,
            interval=3600,  # Every hour in seconds
            first=seconds_until_next_hour,  # Wait until next hour mark
            name='hourly_broadcast'
        )
        
        print(f"📢 Hourly broadcast scheduler enabled!")
        print(f"   Current time: {now_ist.strftime('%I:%M %p')} IST")
        print(f"   Next broadcast: {next_hour_ist.strftime('%I:%M %p')} IST")
        print(f"   Waiting: {int(seconds_until_next_hour / 60)} minutes {int(seconds_until_next_hour % 60)} seconds")
        print(f"   Then every hour at :00 minutes (1:00 PM, 2:00 PM, 3:00 PM, etc.)")
        print()
        
        # Start the bot
        print("=" * 50)
        print("✅ BOTH BOTS ARE RUNNING!")
        print("=" * 50)
        print()
        print("📱 Main Bot: @Videos1_69_bot")
        print("   Purpose: Video distribution")
        print(f"   Channel ID: {CHANNEL_ID}")
        print("   Features: Videos, Premium, Daily Limits")
        print()
        print("💬 Admin Bot: @videos69Admin_Bot")
        print("   Purpose: User support")
        print("   Admin: ")
        print("   Features: Message forwarding, Admin replies")
        print()
        print("🎲 Videos will be sent randomly from the channel!")
        print("📞 Users can contact admin via /help command")
        print()
        
        # Run the bot
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        print(f"\n❌ Error starting bot: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your internet connection")
        print("2. If you're in a region where Telegram is blocked, try using a VPN")
        print("3. Verify your BOT_TOKEN in the .env file is correct")
        print("4. Make sure you have the latest version of python-telegram-bot installed")
        print("5. Try running: pip install --upgrade python-telegram-bot")
        print("\n💡 If the error is 'Timed out', it means the bot cannot reach Telegram servers.")
        print("   This is usually a network/firewall/proxy issue, not a code issue.")


if __name__ == '__main__':
    main()

