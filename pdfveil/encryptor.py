# pdfveil/encryptor.py
import os
from .utils import generate_salt, derive_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def encrypt_pdf(input_path: str, password: str, output_path: str = None):
    """PDFファイルをAES-GCMで暗号化し、.veil.pdfとして保存"""
    
    # 1. PDFを読み込み
    with open(input_path, "rb") as f:
        data = f.read()

    # 2. ソルト & 鍵生成
    salt = generate_salt()
    key = derive_key(password, salt)

    # 3. IV生成（GCM推奨：12バイト）
    iv = os.urandom(12)

    # 4. AES-GCMで暗号化
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    tag = encryptor.tag  # 認証タグ（16バイト）

    # 5. 暗号化ファイルに [salt][iv][ciphertext][tag] を保存
    if not output_path:
        output_path = input_path.replace(".pdf", ".veil.pdf")

    with open(output_path, "wb") as f:
        f.write(salt + iv + ciphertext + tag)

    print(f"[+] Encrypted and saved to: {output_path}")