# Quick Start Guide - Persistent Storage

## 🚀 Ready to Use!

Your bot now has **persistent storage** built-in. No configuration needed!

## ✅ What You Get

- **Premium memberships persist** across bot restarts
- **Video watch history saved** - no duplicate videos
- **Hourly limits maintained** - fair usage continues
- **Automatic data backup** - saved to JSON files
- **Statistics on startup** - see premium users count

## 📝 How to Start

### Option 1: Start Both Bots (Recommended)

```bash
start_bots.bat
```

This starts:
- Main video bot
- Admin support bot

### Option 2: Start Main Bot Only

```bash
python video69_bot.py
```

## 📊 What You'll See on Startup

```
🤖 Starting Videos Bot System...
==================================================

🧹 Cleaning up expired data...

📊 User Statistics:
   Total users: 150
   💎 Premium users: 12
   🆓 Free users: 138
   🎬 Total videos watched: 3,450
   📈 Avg videos per user: 23.0

📂 Loaded states for 150 users from file
💎 Found 12 active premium users

✅ BOTH BOTS ARE RUNNING!
```

## 🧪 Test the System

Run the test script to verify everything works:

```bash
python test_persistent_storage.py
```

Expected output:
```
✅ ALL TESTS PASSED!
💡 The persistent storage system is working correctly!
```

## 📁 Important Files

### Data Files (Auto-Created)
- `users.json` - Basic user information
- `user_states.json` - User states (premium, videos, etc.)

### Code Files
- `video69_bot.py` - Main bot (updated)
- `user_state_storage.py` - Storage module (new)

### Documentation
- `IMPLEMENTATION_SUMMARY.md` - What was done
- `PERSISTENT_STORAGE.md` - How it works
- `VISUAL_GUIDE.md` - Visual diagrams
- `README.md` - General bot info

## 🎯 Common Scenarios

### Scenario 1: User Gets Premium
1. User watches ad
2. Gets 12 hours premium
3. **Bot restarts**
4. ✅ User still has premium!

### Scenario 2: User Watches Videos
1. User watches 50 videos
2. **Bot restarts**
3. ✅ Won't see same videos again!

### Scenario 3: Hourly Limit
1. User watches 7 videos this hour
2. **Bot restarts**
3. ✅ Still has 3 videos remaining!

## 🔧 Maintenance

### Backup Your Data

Regularly backup these files:
```
users.json
user_states.json
```

### Reset User Data

To reset a specific user:
1. Stop the bot
2. Edit `user_states.json`
3. Remove the user's entry
4. Start the bot

To reset all data:
1. Stop the bot
2. Delete `user_states.json`
3. Start the bot

### View Statistics

Statistics are shown on bot startup. To see them again:
1. Restart the bot

## ⚡ Performance

- **Fast startup** - Loads data in seconds
- **No lag** - In-memory caching
- **Automatic saves** - No manual work needed
- **Efficient** - Minimal file I/O

## 🆘 Troubleshooting

### Issue: Premium lost after restart

**This should NOT happen anymore!** If it does:
1. Check if `user_states.json` exists
2. Check if file contains user data
3. Check console for errors

### Issue: Same videos appearing

**This should NOT happen anymore!** If it does:
1. Check if `user_states.json` exists
2. Check if `seen_videos` is being saved
3. Check console for save errors

### Issue: File permission error

**Solution**: Make sure bot has write permissions in its directory.

## 📚 Learn More

- Read `PERSISTENT_STORAGE.md` for detailed explanation
- Read `VISUAL_GUIDE.md` for visual diagrams
- Read `IMPLEMENTATION_SUMMARY.md` for what changed

## ✨ Key Features

```
✅ Premium membership persists
✅ Video history preserved
✅ Hourly limits maintained
✅ Automatic data saving
✅ Statistics on startup
✅ Automatic cleanup
✅ Zero configuration
✅ No maintenance needed
```

## 🎉 You're All Set!

Just start your bot and everything will work automatically!

```bash
python video69_bot.py
```

All user data will be saved and restored across restarts. No more data loss! 🚀
