# [salt(16)][iv(12)][ciphertext(?)][tag(16)]
# pdfveil/decryptor.py
from .utils import derive_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import sys
import os

def is_valid_pdf(file_path: str) -> bool:
    """PDFファイルかどうかを確認する"""
    try:
        with open(file_path, "rb") as f:
            header = f.read(5)
            return header == b"%PDF-"
    except Exception:
        return False

def decrypt_pdf(input_path: str, password: str, output_path: str = None):
    """AES-GCMで暗号化されたPDFを復号して保存"""
    
    # 0. 入力ファイルの拡張子チェック
    if not input_path.lower().endswith(".pdf"):
        print(f"[!] 入力ファイルはPDF (.pdf) 形式である必要があります。")
        sys.exit(1)

    # 1. 暗号化されたファイルを読み込み
    with open(input_path, "rb") as f:
        encrypted_data = f.read()

    # 2. 各データを取り出す
    salt = encrypted_data[:16]
    iv = encrypted_data[16:28]
    tag = encrypted_data[-16:]
    ciphertext = encrypted_data[28:-16]

    # 3. 鍵を導出
    key = derive_key(password, salt)

    # 4. AES-GCMで復号
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    temp_output_path = "temp_decrypted_output.pdf"
    with open(temp_output_path, "wb") as f:
        f.write(decrypted_data)

    if not is_valid_pdf(temp_output_path):
        os.remove(temp_output_path)  # 検証用ファイルを削除
        print("[!] 復号したファイルはPDF形式ではありません。整合性が取れていません。")
        return

    # 5. 出力ファイルに保存
    if not output_path:
        if input_path.endswith(".veil.pdf"):
            output_path = input_path.replace(".veil.pdf", ".decrypted.pdf")
        else:
            output_path = input_path + ".decrypted.pdf"

    with open(output_path, "wb") as f:
        f.write(decrypted_data)
    
    os.remove(temp_output_path)  # 一時ファイルを削除

    print(f"[+] Decrypted and saved to: {output_path}")