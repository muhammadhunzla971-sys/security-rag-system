from fastapi import Header, HTTPException

# Demo ke liye — real production mein ye database mein hoti
VALID_API_KEYS = {
    "tenant1-secret-key-123": "Tenant One",
    "tenant2-secret-key-456": "Tenant Two",
}

def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return VALID_API_KEYS[x_api_key]