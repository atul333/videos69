"""
Test script to verify IST time conversion is working correctly
"""

from datetime import datetime, timedelta, timezone

def utc_to_ist(utc_time):
    """Convert UTC datetime to IST (UTC+5:30)"""
    ist_offset = timedelta(hours=5, minutes=30)
    return utc_time + ist_offset

# Test 1: Current time
print("=" * 50)
print("TEST 1: Current Time Conversion")
print("=" * 50)

current_utc = datetime.now(timezone.utc)
current_ist = utc_to_ist(current_utc)

print(f"Current UTC time: {current_utc.strftime('%I:%M %p')}")
print(f"Current IST time: {current_ist.strftime('%I:%M %p')}")
print(f"Difference: 5 hours 30 minutes")
print()

# Test 2: Premium activation at 8:03 AM IST
print("=" * 50)
print("TEST 2: Premium Activation Example")
print("=" * 50)

# Simulate activation at 8:03 AM IST
# 8:03 AM IST = 2:33 AM UTC (8:03 - 5:30 = 2:33)
activation_utc = datetime(2025, 11, 27, 2, 33, 0, tzinfo=timezone.utc)
activation_ist = utc_to_ist(activation_utc)

print(f"Activation time (UTC): {activation_utc.strftime('%I:%M %p')}")
print(f"Activation time (IST): {activation_ist.strftime('%I:%M %p')}")
print()

# Add 12 hours for premium expiry
expiry_utc = activation_utc + timedelta(hours=12)
expiry_ist = utc_to_ist(expiry_utc)

print(f"Expiry time (UTC): {expiry_utc.strftime('%I:%M %p')}")
print(f"Expiry time (IST): {expiry_ist.strftime('%I:%M %p')}")
print()

# Verify
print("VERIFICATION:")
if activation_ist.strftime('%I:%M %p') == "08:03 AM":
    print("✅ Activation time is correct: 08:03 AM IST")
else:
    print(f"❌ Activation time is wrong: {activation_ist.strftime('%I:%M %p')}")

if expiry_ist.strftime('%I:%M %p') == "08:03 PM":
    print("✅ Expiry time is correct: 08:03 PM IST (12 hours later)")
else:
    print(f"❌ Expiry time is wrong: {expiry_ist.strftime('%I:%M %p')}")

print()
print("=" * 50)
print("All tests completed!")
print("=" * 50)
