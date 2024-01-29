import hashlib


def sha256_hash(input_string: str):
    sha256_hash_obj = hashlib.sha256()
    sha256_hash_obj.update(input_string.encode('utf-8'))
    hashed_string = sha256_hash_obj.hexdigest()

    return hashed_string
