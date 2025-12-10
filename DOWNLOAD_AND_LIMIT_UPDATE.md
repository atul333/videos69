# Video Download and Watch Limit Update

## Summary of Changes

This document describes the changes made to implement the following features:
1. **Allow normal users to download 2 videos**
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

**Lines 611-695:**
- Modified the video sending function to check `downloaded_count`
- For the first 2 videos: `protect_content=False` (allows download/save/forward)
- After 2 videos: `protect_content=True` (prevents download/save/forward)
- Increments `downloaded_count` when a downloadable video is sent
- Shows different messages based on download status:
  - **Video 1**: "💾 You can download/save this video! 📥 Remaining downloads: 1"
  - **Video 2**: "💾 You can download/save this video! 📥 This was your last downloadable video. 🔒 Future videos will be protected."
  - **Video 3+**: "🔒 Download limit reached (2 videos)."

### 4. Broadcast Messages

**Line 470:**
- Updated hourly reset broadcast: "You can now watch **15 free videos**" (was 10)

**Line 597:**
- Updated limit reached message: "You've watched all 15 videos for this hour." (was 10)

## How It Works

### Download Feature
1. When a user requests a video, the bot checks their `downloaded_count`
2. If `downloaded_count < 2`:
   - Video is sent with `protect_content=False` (downloadable)
   - `downloaded_count` is incremented
   - User sees a message indicating they can download the video
3. If `downloaded_count >= 2`:
   - Video is sent with `protect_content=True` (protected)
   - User sees a message indicating download limit is reached

### Watch Limit
1. Free users can watch **15 videos per hour** (increased from 10)
2. The limit resets at the start of each hour
3. Premium users still have unlimited access

## Backward Compatibility

- Existing users who don't have `downloaded_count` in their state will have it automatically initialized to `0` when they request their next video
- This ensures the feature works for both new and existing users

## Testing Recommendations

1. **New User Test:**
   - Start the bot with a new user
   - Request 3 videos
   - Verify first 2 are downloadable, 3rd is protected

2. **Existing User Test:**
   - Use an existing user account
   - Request a video
   - Verify `downloaded_count` is initialized automatically

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
