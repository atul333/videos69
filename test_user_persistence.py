# -*- coding: utf-8 -*-
"""
Test script to verify users.json persistence
This script simulates bot restarts and checks if user data persists
"""

import json
import os
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

USERS_FILE = "users.json"

def load_users():
    """Load users from file"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            users = json.load(f)
            print(f"✅ Loaded {len(users)} users from file:")
            for user in users:
                print(f"   - {user['first_name']} (ID: {user['user_id']})")
            return users
    else:
        print("❌ No users.json file found!")
        return []

def save_users(users_data):
    """Save users to file"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_data, f, indent=2, ensure_ascii=False)
    print(f"💾 Saved {len(users_data)} users to file")

def add_test_user(users_data, user_id, first_name):
    """Add a test user"""
    # Check if user already exists
    for user in users_data:
        if user['user_id'] == user_id:
            print(f"⚠️ User {first_name} already exists, skipping")
            return users_data
    
    # Add new user
    new_user = {
        'user_id': user_id,
        'first_name': first_name,
        'username': f"test_{user_id}",
        'joined_date': "2025-11-30T00:00:00+00:00",
        'last_seen': "2025-11-30T00:00:00+00:00"
    }
    users_data.append(new_user)
    print(f"✅ Added test user: {first_name} (ID: {user_id})")
    return users_data

# Test 1: Load existing users
print("=" * 50)
print("TEST 1: Loading existing users from file")
print("=" * 50)
users = load_users()
print()

# Test 2: Simulate bot restart (reload from file)
print("=" * 50)
print("TEST 2: Simulating bot restart (reload from file)")
print("=" * 50)
users = load_users()
print()

# Test 3: Add a test user and save
print("=" * 50)
print("TEST 3: Adding test user and saving")
print("=" * 50)
users = add_test_user(users, 999999999, "Test User")
save_users(users)
print()

# Test 4: Reload to verify persistence
print("=" * 50)
print("TEST 4: Reloading to verify persistence")
print("=" * 50)
users = load_users()
print()

print("=" * 50)
print("✅ TEST COMPLETE!")
print("=" * 50)
print()
print("📋 Summary:")
print(f"   - Total users in database: {len(users)}")
print(f"   - File location: {os.path.abspath(USERS_FILE)}")
print()
print("💡 If you see your existing users above, the file is NOT resetting!")
print("   The cache variables reset on bot restart, but the FILE persists.")
