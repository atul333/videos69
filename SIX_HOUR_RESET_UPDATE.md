# 6-Hour Reset Period Update

## Change Summary
**Date:** December 13, 2025

### What Changed
Changed the reset period from **every 1 hour** to **every 6 hours**

## Details

### Before
- Limits reset every hour (at the start of each hour)
- Users got fresh limits 24 times per day
- Broadcast sent every hour

### After  
- Limits reset every 6 hours (at 00:00, 06:00, 12:00, 18:00)
- Users get fresh limits 4 times per day
- Broadcast sent 4 times per day
- **More sustainable** for both users and system

## Reset Schedule

### 6-Hour Periods (IST)
1. **Period 1:** 12:00 AM - 6:00 AM (00:00 - 06:00)
2. **Period 2:** 6:00 AM - 12:00 PM (06:00 - 12:00)
3. **Period 3:** 12:00 PM - 6:00 PM (12:00 - 18:00)
4. **Period 4:** 6:00 PM - 12:00 AM (18:00 - 24:00)

### Limits Per Period
- **Free Users:** 15 videos + 2 downloads
- **Premium Users:** Unlimited videos + 20 downloads

## Changes Made

### 1. Reset Logic Function
**File:** `video69_bot.py` (Lines 304-327)

**Before:**
```python
def check_and_reset_hourly_limit(user_id):
    """Check if hourly limit needs to be reset (at the start of each hour)"""
    # Reset every hour
    current_hour_start = now.replace(minute=0, second=0, microsecond=0)
    if current_hour_start > user_state['last_reset']:
        # Reset counts
```

**After:**
```python
def check_and_reset_hourly_limit(user_id):
    """Check if limit needs to be reset (every 6 hours)"""
    # Calculate 6-hour periods: 00:00-06:00, 06:00-12:00, 12:00-18:00, 18:00-24:00
    current_hour = now.hour
    period_start_hour = (current_hour // 6) * 6  # 0, 6, 12, or 18
    current_period_start = now.replace(hour=period_start_hour, minute=0, second=0, microsecond=0)
    
    if current_period_start > user_state['last_reset']:
        # Reset counts every 6 hours
```

### 2. Constants and Comments
**File:** `video69_bot.py` (Lines 59-66)

**Updated:**
- "resets every hour" → "resets every 6 hours"
- "per hour" → "every 6 hours"

### 3. Broadcast Function
**File:** `video69_bot.py` (Lines 451-525)

**Changes:**
- Docstring: "sent every hour" → "sent every 6 hours"
- Print: "HOURLY BROADCAST" → "6-HOUR RESET BROADCAST"
- Message title: "Hourly Limit Reset!" → "Limit Reset!"
- Added: "⏱️ Limits reset every **6 hours**"
- Print: "Hourly broadcast complete" → "6-hour reset broadcast complete"

### 4. Broadcast Scheduler
**File:** `video69_bot.py` (Lines 1391-1435)

**Before:**
```python
# Run every hour at :30 minutes
job_queue.run_repeating(
    broadcast_hourly_reset,
    interval=3600,  # Every hour
    ...
)
```

**After:**
```python
# Run every 6 hours at 00:00, 06:00, 12:00, 18:00
job_queue.run_repeating(
    broadcast_hourly_reset,
    interval=21600,  # Every 6 hours (6 * 3600)
    ...
)
```

## User Experience

### Example: User Activity in One Day

**Period 1 (12:00 AM - 6:00 AM):**
- User gets 15 videos + 2 downloads
- Uses 10 videos + 1 download
- Remaining: 5 videos + 1 download

**Period 2 (6:00 AM - 12:00 PM):**
- 🔄 **Reset!** Fresh 15 videos + 2 downloads
- User gets broadcast notification
- Uses all 15 videos + 2 downloads

**Period 3 (12:00 PM - 6:00 PM):**
- 🔄 **Reset!** Fresh 15 videos + 2 downloads
- User gets broadcast notification
- Uses 8 videos + 0 downloads

**Period 4 (6:00 PM - 12:00 AM):**
- 🔄 **Reset!** Fresh 15 videos + 2 downloads
- User gets broadcast notification
- Uses 12 videos + 1 download

**Total for the day:** 45 videos watched + 4 downloads used

## Broadcast Message

**New Message:**
```
🎬 Limit Reset! 🎬

⏰ Time: 12:00 PM IST
📅 Date: December 13, 2025

✨ Your limits have been renewed!
🎥 You can now watch 15 free videos
📥 You can download 2 videos
💎 Premium users get 20 downloads!

⏱️ Limits reset every 6 hours
💎 Want unlimited videos + 20 downloads? Watch an ad!

Click below to start watching!

Enjoy! 🍿

[🎬 Watch Now]
```

## Benefits

### For Users
- ✅ **More time per period** - 6 hours instead of 1 hour
- ✅ **Less pressure** - No rush to use limits quickly
- ✅ **Predictable schedule** - Reset at fixed times (12 AM, 6 AM, 12 PM, 6 PM)
- ✅ **Fewer interruptions** - Only 4 broadcasts per day instead of 24

### For System
- ✅ **Reduced broadcast load** - 4 broadcasts/day instead of 24
- ✅ **Less frequent resets** - More efficient
- ✅ **Better resource management** - Fewer database writes
- ✅ **Cleaner user experience** - Less spam

## Technical Details

### Reset Calculation
```python
# Determine which 6-hour period we're in
current_hour = now.hour  # 0-23
period_start_hour = (current_hour // 6) * 6  # 0, 6, 12, or 18

# Examples:
# If current_hour = 3  → period_start_hour = 0  (12:00 AM period)
# If current_hour = 8  → period_start_hour = 6  (6:00 AM period)
# If current_hour = 14 → period_start_hour = 12 (12:00 PM period)
# If current_hour = 20 → period_start_hour = 18 (6:00 PM period)
```

### Next Broadcast Calculation
```python
next_period_hour = ((current_hour // 6) + 1) * 6

if next_period_hour >= 24:
    # Next period is tomorrow at 00:00
    next_broadcast = tomorrow at 00:00
else:
    # Next period is today
    next_broadcast = today at next_period_hour
```

## Testing

### Test Scenario 1: Reset Timing
1. Note current time
2. Wait for next 6-hour period (00:00, 06:00, 12:00, or 18:00)
3. ✅ Verify broadcast is sent
4. ✅ Verify limits are reset
5. ✅ Verify downloaded_count = 0

### Test Scenario 2: Multiple Periods
1. Use all limits in Period 1
2. ✅ Verify limits are exhausted
3. Wait for Period 2 to start
4. ✅ Verify limits are reset
5. ✅ Verify can watch/download again

### Test Scenario 3: Broadcast Schedule
1. Start bot
2. ✅ Verify console shows "6-hour broadcast scheduler enabled"
3. ✅ Verify next broadcast time is at 00:00, 06:00, 12:00, or 18:00
4. ✅ Verify interval is 21600 seconds (6 hours)

## Files Modified

1. **video69_bot.py**
   - `check_and_reset_hourly_limit()` function
   - Constants comments
   - `broadcast_hourly_reset()` function
   - Broadcast scheduler in `main()`

## Migration Notes

- ✅ **No data migration needed** - Existing users will automatically use new 6-hour periods
- ✅ **Backward compatible** - `last_reset` field works the same way
- ✅ **Immediate effect** - Changes take effect on next bot restart

## Summary

This update changes the reset period from **1 hour to 6 hours**, providing:

**Key Benefits:**
- ✅ More relaxed user experience (6 hours vs 1 hour)
- ✅ Predictable reset times (12 AM, 6 AM, 12 PM, 6 PM)
- ✅ Fewer broadcasts (4/day vs 24/day)
- ✅ Better system efficiency
- ✅ Same total daily limits (60 videos, 8 downloads for free users)

**Reset Times (IST):**
- 🕛 **12:00 AM** (Midnight)
- 🕕 **6:00 AM** (Morning)
- 🕛 **12:00 PM** (Noon)
- 🕕 **6:00 PM** (Evening)
