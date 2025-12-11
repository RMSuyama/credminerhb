import bcrypt
import sqlite3
from src.database import get_connection

def check_credentials(username, password):
    """Verifies username and password."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        stored_hash = result[0].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
            return True
    return False

import hmac
import hashlib
import base64
import json
import time

SECRET_KEY = "my_super_secret_key_change_this_in_production"

def create_session_token(username):
    """Creates a signed token for the username."""
    # Data to sign
    payload = {
        "user": username,
        "exp": time.time() + (7 * 24 * 3600) # 7 days expiration
    }
    payload_str = json.dumps(payload)
    payload_b64 = base64.urlsafe_b64encode(payload_str.encode()).decode()
    
    # Signature
    signature = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
    
    return f"{payload_b64}.{signature}"

def validate_session_token(token):
    """Validates the token and returns the username if valid."""
    try:
        if not token or "." not in token:
            return None
            
        payload_b64, signature = token.split(".")
        
        # Verify Signature
        expected_sig = hmac.new(SECRET_KEY.encode(), payload_b64.encode(), hashlib.sha256).hexdigest()
        
        if hmac.compare_digest(signature, expected_sig):
            # Decode payload
            payload_str = base64.urlsafe_b64decode(payload_b64).decode()
            payload = json.loads(payload_str)
            
            # Check expiration
            if payload.get("exp", 0) > time.time():
                return payload.get("user")
    except Exception as e:
        print(f"Token validation error: {e}")
        return None
    return None
