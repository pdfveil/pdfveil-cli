# pdfveil/utils.py
# 1. ソルトを生成（または受け取る）
# 2. PBKDF2HMAC でパスワード → 鍵を生成
# 3. 32バイト（AES-256）鍵を返す

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def generate_salt(length: int = 16) -> bytes:
    """ランダムなソルトを生成"""
    return os.urandom(length)

def derive_key(password: str, salt: bytes, iterations: int = 200_000) -> bytes:
    """パスワードとソルトからAES鍵（32バイト）を導出"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256 = 32バイト鍵
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode())