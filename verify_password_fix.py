import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

import auth

def test_passwords():
    test_cases = [
        "short",
        "standard_password_123",
        "a" * 72,
        "a" * 73,
        "a" * 150,
        "very_long_password_with_lots_of_characters_to_exceed_seventy_two_bytes_limit_1234567890!@#$%^&*()"
    ]

    for pw in test_cases:
        print(f"\nTesting password (len={len(pw)}): {pw[:20]}...")
        try:
            hashed = auth.get_password_hash(pw)
            print(f"Hash generated successfully.")
            
            # Verify
            is_valid = auth.verify_password(pw, hashed)
            print(f"Verification: {'SUCCESS' if is_valid else 'FAILED'}")
            
            # Negative test
            is_invalid = auth.verify_password(pw + "_wrong", hashed)
            print(f"Negative Verification (wrong pw): {'SUCCESS' if not is_invalid else 'FAILED'}")
            
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    test_passwords()
