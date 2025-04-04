# pdfveil/utils.py
# 1. ソルトを生成（または受け取る）
# 2. PBKDF2HMAC でパスワード → 鍵を生成
# 3. 32バイト（AES-256）鍵を返す

import os
import re
import getpass
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

def is_strong_password(password: str) -> bool:
    """強力なパスワードかどうかを検証 (12文字以上、大小文字、数字、特殊文字を含む)"""
    return bool(re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{12,}$', password))

def generate_salt(length: int = 16) -> bytes:
    """ランダムなソルトを生成"""
    return os.urandom(length)

def derive_key(password: str, salt: bytes, mode: str, iterations: int = 500_000) -> bytes:
    """パスワードとソルトからAES鍵（32バイト）を導出"""
    if mode == 'enc' and not is_strong_password(password):
        # パスワードが強力でない場合にユーザーに確認を取る
        while True:
            user_response = input("[!] パスワードが強力ではありませんが、このまま暗号化しますか？ (Yes/No): ").strip().lower()
            if user_response == 'yes':
                break  # 暗号化を続行
            elif user_response == 'no':
                password = getpass.getpass("🔑 Enter password: ")
                if is_strong_password(password):
                    break  # 新しい強力なパスワードで再試行
                else:
                    print("[!] 強力なパスワードが必要です。再度入力してください。")
            else:
                print("[!] 'Yes' か 'No' を入力してください。")
    
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,  # AES-256 = 32バイト鍵
        salt=salt,
        iterations=iterations,
    )
    return kdf.derive(password.encode())