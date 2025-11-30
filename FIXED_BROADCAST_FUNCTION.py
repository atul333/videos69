# FIXED BROADCAST FUNCTION
# Replace the broadcast_hourly_reset function in video69_bot.py with this version

async def broadcast_hourly_reset(context: ContextTypes.DEFAULT_TYPE):
    """Broadcast message ONLY to users whose hourly limit is being reset"""
    
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
    
    # Get current hour start for reset check
    now_utc = datetime.now(timezone.utc)
    current_hour_start = now_utc.replace(minute=0, second=0, microsecond=0)
    
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
    
    # Send broadcast and reset counts
    successful = 0
    failed = 0
    skipped = 0
    blocked_users = []
    reset_count = 0
    
    for user_id in user_ids:
        # Check if user needs reset (only send broadcast if they do)
        needs_reset = False
        
        if user_id in user_states:
            user_state = user_states[user_id]
            
            # Skip premium users - they don't have hourly limits
            if is_premium_user(user_id):
                skipped += 1
                continue
            
            # Check if user's limit needs to be reset
            if current_hour_start > user_state['last_reset']:
                # User's hour has changed - check if they watched any videos
                if user_state['hourly_count'] > 0:
                    # User watched videos in previous hour - send broadcast
                    needs_reset = True
                    # Reset their count
                    user_state['hourly_count'] = 0
                    user_state['last_reset'] = current_hour_start
                    reset_count += 1
                else:
                    # User didn't watch any videos - don't send broadcast
                    # But still update their last_reset time
                    user_state['last_reset'] = current_hour_start
                    skipped += 1
            else:
                # Same hour - no reset needed
                skipped += 1
        else:
            # User not in memory yet - skip broadcast
            skipped += 1
            continue
        
        # Only send broadcast if user needs reset
        if needs_reset:
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
    
    print(f"📢 Hourly broadcast complete!")
    print(f"   ✅ Sent to {successful} users (who watched videos in previous hour)")
    print(f"   ⏭️ Skipped {skipped} users (premium, no videos watched, or not in memory)")
    print(f"   ❌ Failed: {failed} users")
    print(f"   🔄 Reset count for {reset_count} users")
    print(f"⏰ Broadcast time: {time_str} IST")
    print(f"📅 Broadcast date: {date_str}")
    print(f"👥 Total users in database: {get_user_count()}")
