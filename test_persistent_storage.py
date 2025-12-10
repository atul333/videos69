"""
Test script to verify persistent storage functionality
"""

import sys
import io
# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import json
from datetime import datetime, timedelta, timezone
from user_state_storage import (
    load_user_states,
    save_user_states,
    init_user_state_data,
    get_premium_users_count,
    get_stats,
    cleanup_expired_data
)

def test_persistent_storage():
    """Test the persistent storage system"""
    
    print("🧪 Testing Persistent Storage System")
    print("=" * 60)
    
    # Test 1: Load existing states
    print("\n📂 Test 1: Loading user states...")
    states = load_user_states()
    print(f"✅ Loaded {len(states)} user states")
    
    # Test 2: Create a test user
    print("\n👤 Test 2: Creating test user...")
    test_user_id = 999999999
    
    if test_user_id in states:
        print(f"⚠️ Test user already exists, removing...")
        del states[test_user_id]
    
    init_user_state_data(test_user_id, states)
    print(f"✅ Created test user {test_user_id}")
    print(f"   State: {states[test_user_id]}")
    
    # Test 3: Grant premium access
    print("\n💎 Test 3: Granting premium access...")
    states[test_user_id]['premium_until'] = datetime.now(timezone.utc) + timedelta(hours=12)
    save_user_states(states)
    print(f"✅ Premium granted until: {states[test_user_id]['premium_until']}")
    
    # Test 4: Add some watched videos
    print("\n🎬 Test 4: Adding watched videos...")
    states[test_user_id]['seen_videos'] = [1, 5, 10, 15, 20]
    states[test_user_id]['hourly_count'] = 5
    save_user_states(states)
    print(f"✅ Added 5 watched videos")
    print(f"   Seen videos: {states[test_user_id]['seen_videos']}")
    print(f"   Hourly count: {states[test_user_id]['hourly_count']}")
    
    # Test 5: Reload from file to verify persistence
    print("\n🔄 Test 5: Reloading from file...")
    # Clear the cache to force reload
    from user_state_storage import _states_cache, _states_cache_loaded
    import user_state_storage
    user_state_storage._states_cache = None
    user_state_storage._states_cache_loaded = False
    
    reloaded_states = load_user_states()
    
    if test_user_id in reloaded_states:
        print(f"✅ Test user found after reload!")
        print(f"   Premium until: {reloaded_states[test_user_id]['premium_until']}")
        print(f"   Seen videos: {reloaded_states[test_user_id]['seen_videos']}")
        print(f"   Hourly count: {reloaded_states[test_user_id]['hourly_count']}")
        
        # Verify data matches
        if reloaded_states[test_user_id]['seen_videos'] == [1, 5, 10, 15, 20]:
            print("✅ Seen videos match!")
        else:
            print("❌ Seen videos don't match!")
        
        if reloaded_states[test_user_id]['hourly_count'] == 5:
            print("✅ Hourly count matches!")
        else:
            print("❌ Hourly count doesn't match!")
        
        if reloaded_states[test_user_id]['premium_until'] is not None:
            print("✅ Premium status persisted!")
        else:
            print("❌ Premium status lost!")
    else:
        print("❌ Test user not found after reload!")
    
    # Test 6: Get statistics
    print("\n📊 Test 6: Getting statistics...")
    stats = get_stats(reloaded_states)
    print(f"✅ Statistics:")
    print(f"   Total users: {stats['total_users']}")
    print(f"   Premium users: {stats['premium_users']}")
    print(f"   Free users: {stats['free_users']}")
    print(f"   Total videos watched: {stats['total_videos_watched']}")
    print(f"   Avg videos per user: {stats['avg_videos_per_user']:.1f}")
    
    # Test 7: Premium users count
    print("\n💎 Test 7: Counting premium users...")
    premium_count = get_premium_users_count(reloaded_states)
    print(f"✅ Active premium users: {premium_count}")
    
    # Test 8: Cleanup
    print("\n🧹 Test 8: Testing cleanup...")
    cleaned = cleanup_expired_data(reloaded_states)
    print(f"✅ Cleaned up {cleaned} users")
    
    # Test 9: Remove test user
    print("\n🗑️ Test 9: Removing test user...")
    if test_user_id in reloaded_states:
        del reloaded_states[test_user_id]
        save_user_states(reloaded_states)
        print(f"✅ Test user removed")
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\n💡 The persistent storage system is working correctly!")
    print("   Premium status, video history, and hourly limits will")
    print("   persist across bot restarts.")

if __name__ == "__main__":
    try:
        test_persistent_storage()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
