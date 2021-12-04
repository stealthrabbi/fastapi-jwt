import time
from typing import Dict

import jwt
from decouple import config

# TODO rather than reading this from .env, should htis simply be set statically to a random value, e.g. a new UUID? it would change each time the webapp restarted
# and cause all existing tokens to be invalidated
JWT_SECRET = config("secret")
JWT_ALGORITHM = config("algorithm")
TOKEN_EXPIRATION_SECONDS = 600

def token_response(token: str):
    return {
        "access_token": token,
        "role": "dummy-role"
    }


def signJWT(user_id: str) -> Dict[str, str]:
    payload = {
        "user_id": user_id,
        "expires": time.time() + TOKEN_EXPIRATION_SECONDS
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return token_response(token)


def decodeJWT(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        # MPF I added some logging 

        expiration_time = decoded_token["expires"] 
        current_time = time.time()
        print("user_id: " + decoded_token["user_id"])
        print("expiration_time: " + str(expiration_time))
        print("current_time: " + str(current_time))
        if current_time >= expiration_time:
            print("Token expired on " + str(expiration_time))
            return None

        return decoded_token
    except BaseException as error:
        print('JWT decode exception: {}'.format(error))
