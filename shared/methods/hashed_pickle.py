import pickle
import hmac
import hashlib
import json
import logging
import base64


main_log = logging.getLogger("MAIN_LOG")

def sign_message(unique_key:str, data_to_hash):
    """Uses pickle and hashlib and hmac in order to sign data that is sent
    betweeen client and server"""
    pickled_data = pickle.dumps(data_to_hash)
    digest = hmac.new(unique_key.encode('utf-8'), pickled_data, hashlib.blake2b).hexdigest()
    pickle_decoded = base64.b64encode(pickled_data).decode('utf-8')

    signed_data = {
        "signature":digest,
        "data":pickle_decoded}
    return signed_data


def verified_message(unique_key:str, received_message):
    """Uses pickle and hashlib and hmac in order to check if data that is sent
    betweeen client and server has proper key"""
    signature = received_message['signature'] 
    decoded_data = received_message['data']
    data = base64.b64decode(decoded_data)    

    digest = hmac.new(unique_key.encode('utf-8'), data, hashlib.blake2b).hexdigest()

    if not hmac.compare_digest(digest, signature):
        raise ValueError("HMAC signatures do not match")
    
    unpickled_data = pickle.loads(data)
    return unpickled_data


