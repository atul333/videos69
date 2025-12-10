# Video Download and Watch Limit Update

## Summary of Changes

This document describes the changes made to implement the following features:
1. **Allow normal users to download 2 videos (on-demand via Download button)**
2. **Increase watch limit from 10 to 15 videos per hour**

## Changes Made

### 1. Configuration Constants (video69_bot.py)

**Lines 59-64:**
- Changed `HOURLY_VIDEO_LIMIT` from `10` to `15`
- Added new constant `DOWNLOADABLE_VIDEOS_LIMIT = 2`

```python
# Hourly video limit for free users (resets every hour)
HOURLY_VIDEO_LIMIT = 15
# Premium access duration after watching ad (12 hours)
PREMIUM_DURATION_HOURS = 12
# Number of videos that can be downloaded/saved by normal users
DOWNLOADABLE_VIDEOS_LIMIT = 2
```

### 2. User State Storage (user_state_storage.py)

**Lines 127-148:**
- Added `downloaded_count` field to track how many videos each user has downloaded
- This field is initialized to `0` for new users

```python
new_state = {
    'seen_videos': [],
    'hourly_count': 0,
    'last_reset': last_reset,
    'premium_until': None,
    'ad_link': None,
    'ad_token': None,
    'downloaded_count': 0  # Track number of videos downloaded
}
```

### 3. Video Sending Logic (video69_bot.py)

**Lines 611-685:**
- **All videos are sent with `protect_content=True` (protected by default)**
- Shows a **"📥 Download" button** if user has downloads remaining
- Button shows remaining downloads: "📥 Download (2 left)", "📥 Download (1 left)"
- When user clicks Download button:
  - Sends an unprotected copy of the video (can be saved/forwarded)
  - Increments `downloaded_count`
  - Updates button to show new remaining count
  - After 2 downloads, button is removed

### 4. Download Button Handler (video69_bot.py)

**Lines 1124-1237:**
- Added new callback handler for `download_` button clicks
- Validates user has downloads remaining
- Sends unprotected copy of the video
- Updates the original message with new download count
- Sends confirmation message
- Removes Download button after 2 downloads

### 5. Broadcast Messages

**Line 470:**
- Updated hourly reset broadcast: "You can now watch **15 free videos**" (was 10)

**Line 597:**
- Updated limit reached message: "You've watched all 15 videos for this hour." (was 10)

**Line 1027:**
- Updated membership verification: "You can watch **15 videos per hour** for free!" (was 10)

## How It Works

### Download Feature (On-Demand)
1. **All videos are protected by default** - users cannot download/save/forward initially
2. **Download button appears** below each video if user has downloads remaining
3. **User clicks Download button** when they want to save a specific video
4. **Bot sends unprotected copy** of that video (can be downloaded/saved/forwarded)
5. **Download count increments** and button updates to show remaining downloads
6. **After 2 downloads**, the Download button is removed from all future videos

### Watch Limit
1. Free users can watch **15 videos per hour** (increased from 10)
2. The limit resets at the start of each hour
3. Premium users still have unlimited access

## Backward Compatibility

- Existing users who don't have `downloaded_count` in their state will have it automatically initialized to `0` when they request their next video
- This ensures the feature works for both new and existing users

## Testing Recommendations

1. **Download Button Test:**
   - Start the bot with a new user
   - Request a video
   - Verify Download button appears with "(2 left)"
   - Click Download button
   - Verify unprotected copy is sent
   - Verify button updates to "(1 left)"
   - Click Download button again
   - Verify second unprotected copy is sent
   - Verify Download button disappears
   - Request another video
   - Verify no Download button appears

2. **Existing User Test:**
   - Use an existing user account
   - Request a video
   - Verify `downloaded_count` is initialized automatically
   - Verify Download button appears

3. **Watch Limit Test:**
   - Watch 15 videos in one hour
   - Verify limit reached message shows "15 videos"
   - Wait for hourly reset
   - Verify broadcast message shows "15 free videos"

## Files Modified

1. `video69_bot.py` - Main bot logic
2. `user_state_storage.py` - User state initialization

## Date
December 10, 2025
