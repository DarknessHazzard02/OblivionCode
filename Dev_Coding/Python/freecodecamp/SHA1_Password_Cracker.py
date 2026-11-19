# Author: Haz
# FreeCodeCamp Information Security with Python - SHA-1 Password Cracker
# Verifies password hashes against common dictionary lists and salted variations

import hashlib

SAMPLE_PASSWORDS = [
    "password", "123456", "12345678", "1234", "qwerty",
    "12345", "dragon", "pussy", "baseball", "football",
    "monkey", "letmein", "superman", "master", "shadow",
    "mustang", "trustno1", "michael", "hazzard", "oblivion"
]

KNOWN_SALTS = ["supersecret", "salt123", "fcc_salt", "pepper99"]

def crack_sha1_hash(hash_to_crack, use_salts=False, wordlist=None):
    passwords = wordlist or SAMPLE_PASSWORDS
    salts = KNOWN_SALTS if use_salts else [""]

    for password in passwords:
        if not use_salts:
            candidate_hash = hashlib.sha1(password.encode("utf-8")).hexdigest()
            if candidate_hash == hash_to_crack:
                return password
        else:
            for salt in salts:
                # Try prepend: salt + password
                prepended = f"{salt}{password}"
                if hashlib.sha1(prepended.encode("utf-8")).hexdigest() == hash_to_crack:
                    return password

                # Try append: password + salt
                appended = f"{password}{salt}"
                if hashlib.sha1(appended.encode("utf-8")).hexdigest() == hash_to_crack:
                    return password

    return "PASSWORD NOT IN DATABASE"

# Demonstration Tests
if __name__ == "__main__":
    print("=== SHA-1 Password Cracker Verification ===")

    # Test 1: Plain SHA-1 hash for 'password'
    target1 = hashlib.sha1(b"password").hexdigest()
    print(f"Target Hash (password): {target1}")
    print(f"Cracked Result:         {crack_sha1_hash(target1)}")

    # Test 2: Plain SHA-1 hash for 'superman'
    target2 = hashlib.sha1(b"superman").hexdigest()
    print(f"\nTarget Hash (superman): {target2}")
    print(f"Cracked Result:         {crack_sha1_hash(target2)}")

    # Test 3: Salted SHA-1 hash for 'hazzard' with salt 'fcc_salt'
    salted_hazzard = hashlib.sha1(b"fcc_salthazzard").hexdigest()
    print(f"\nTarget Hash (fcc_salthazzard): {salted_hazzard}")
    print(f"Cracked with Salts:            {crack_sha1_hash(salted_hazzard, use_salts=True)}")
