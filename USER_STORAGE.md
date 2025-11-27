# User Data Storage System

## Overview
The bot now stores all user data in a persistent JSON file (`users.json`). This ensures user data is not lost when the bot restarts.

## File Structure

### users.json
```json
[
  {
    "user_id": 123456789,
    "first_name": "John",
    "username": "john_doe",
    "joined_date": "2025-11-27T04:44:29.123456+00:00",
    "last_seen": "2025-11-27T04:44:29.123456+00:00"
  },
  {
    "user_id": 987654321,
    "first_name": "Jane",
    "username": "jane_smith",
    "joined_date": "2025-11-27T05:30:15.789012+00:00",
    "last_seen": "2025-11-27T05:30:15.789012+00:00"
  }
]
```

## Features

### 1. **Persistent Storage**
- All user data saved to `users.json` file
- Data survives bot restarts
- Automatic file creation if doesn't exist

### 2. **Duplicate Prevention**
- Checks if user already exists before adding
- Uses `user_id` as unique identifier
- No duplicate entries possible

### 3. **Automatic Updates**
- Updates user's name if changed
- Updates username if changed
- Updates `last_seen` timestamp
- Preserves original `joined_date`

### 4. **Data Tracked**
- **user_id**: Telegram user ID (unique)
- **first_name**: User's first name
- **username**: Telegram username (optional)
- **joined_date**: When user first started the bot (ISO format)
- **last_seen**: Last time user interacted (ISO format)

## Functions

### load_users_from_file()
```python
# Load all users from JSON file
users_data = load_users_from_file()
# Returns: List of user dictionaries
```

### save_users_to_file(users_data)
```python
# Save users to JSON file
save_users_to_file(users_data)
# Saves with pretty formatting (indent=2)
```

### add_user_to_file(user_id, first_name, username)
```python
# Add new user or update existing
is_new = add_user_to_file(123456789, "John", "john_doe")
# Returns: True if new user, False if updated existing
```

### get_all_user_ids()
```python
# Get list of all user IDs
user_ids = get_all_user_ids()
# Returns: [123456789, 987654321, ...]
```

## How It Works

### When User Starts Bot
```python
# In start_command()
user_id = user.id
first_name = user.first_name
username = user.username

# Save to file (checks for duplicates automatically)
add_user_to_file(user_id, first_name, username)
```

**Flow:**
1. User sends `/start`
2. Bot extracts user info
3. Checks if user exists in file
4. If new: Adds to file with joined_date
5. If exists: Updates name/username and last_seen

### Daily Broadcast (12:00 AM IST)
```python
# In broadcast_new_videos()
# Load all user IDs from file
user_ids = get_all_user_ids()

# Send message to each user
for user_id in user_ids:
    send_message(user_id, message)
```

**Flow:**
1. Broadcast triggered at 12:00 AM
2. Loads all user IDs from file
3. Sends message to each user
4. Tracks blocked users
5. Removes blocked users from file

### Blocked User Cleanup
```python
# During broadcast
if user blocked bot:
    blocked_users.append(user_id)

# After broadcast
users_data = [u for u in users_data if u['user_id'] not in blocked_users]
save_users_to_file(users_data)
```

## Benefits

### ✅ **Data Persistence**
- Users not lost on bot restart
- Survives server crashes
- Reliable user database

### ✅ **No Duplicates**
- Automatic duplicate checking
- Uses user_id as unique key
- Clean, organized data

### ✅ **Automatic Cleanup**
- Removes blocked users
- Keeps file clean
- Reduces failed broadcasts

### ✅ **Easy Backup**
- Simple JSON format
- Human-readable
- Easy to backup/restore

### ✅ **Broadcast Reliability**
- Always has complete user list
- Works after bot restart
- No users missed

## File Operations

### On Bot Startup
```
📂 Loaded 150 users from file
```

### When New User Starts Bot
```
✅ Added new user: John (ID: 123456789)
💾 Saved 151 users to file
```

### When Existing User Returns
```
🔄 Updated user: John (ID: 123456789)
💾 Saved 151 users to file
```

### During Broadcast
```
📢 Daily broadcast complete! Sent to 145 users, 5 failed
🗑️ Removed 3 blocked users from file
💾 Saved 148 users to file
```

## Example User Journey

### Day 1
```
User sends /start
→ Bot creates entry in users.json:
{
  "user_id": 123456789,
  "first_name": "John",
  "username": "john_doe",
  "joined_date": "2025-11-27T10:00:00+00:00",
  "last_seen": "2025-11-27T10:00:00+00:00"
}
```

### Day 2
```
Bot restarts
→ Loads users.json
→ John's data still there!

User sends /start again
→ Updates last_seen:
{
  "user_id": 123456789,
  "first_name": "John",
  "username": "john_doe",
  "joined_date": "2025-11-27T10:00:00+00:00",  ← Preserved
  "last_seen": "2025-11-28T08:30:00+00:00"     ← Updated
}
```

### Day 3
```
User changes name to "Johnny"
→ Updates first_name:
{
  "user_id": 123456789,
  "first_name": "Johnny",                      ← Updated
  "username": "john_doe",
  "joined_date": "2025-11-27T10:00:00+00:00",  ← Preserved
  "last_seen": "2025-11-29T12:15:00+00:00"     ← Updated
}
```

### Day 4
```
User blocks bot
→ Broadcast fails
→ User removed from users.json
→ File now has 147 users (was 148)
```

## File Location

```
d:\Videos69 bot\
├── bot.py
├── users.json          ← User data file
├── .env
└── requirements.txt
```

## Backup Recommendation

**Manual Backup:**
```bash
# Copy users.json to backup location
copy users.json users_backup_2025-11-27.json
```

**Automatic Backup (Optional):**
- Could add daily backup function
- Save to `backups/users_YYYY-MM-DD.json`
- Keep last 7 days of backups

## Error Handling

### File Not Found
```python
# Creates empty file automatically
if not os.path.exists(USERS_FILE):
    return []  # Start fresh
```

### Corrupted JSON
```python
# Catches JSON errors
except Exception as e:
    print(f"⚠️ Error loading users file: {e}")
    return []  # Start fresh
```

### Save Errors
```python
# Logs but doesn't crash
except Exception as e:
    print(f"⚠️ Error saving users file: {e}")
```

## Statistics

You can easily get user statistics from the file:

```python
users_data = load_users_from_file()

# Total users
total = len(users_data)

# Users with username
with_username = len([u for u in users_data if u.get('username')])

# Joined today
today = datetime.now(timezone.utc).date()
joined_today = len([u for u in users_data 
                    if datetime.fromisoformat(u['joined_date']).date() == today])
```

## Summary

The bot now has a **robust, persistent user storage system** that:
- ✅ Saves all user data to file
- ✅ Prevents duplicates
- ✅ Survives restarts
- ✅ Auto-updates user info
- ✅ Cleans up blocked users
- ✅ Powers reliable broadcasts

All user data is safe and persistent! 🎉
