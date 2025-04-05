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

def decrypt_pdf(input_path: str, password: str, output_path: str = None, force: bool = False):
    """AES-GCMで暗号化されたPDFを復号して保存"""
    
    # 0. 入力ファイルの拡張子チェック
    if not input_path.lower().endswith(".veil"):
        print(f"[!] 入力ファイルはVEIL (.veil) 形式である必要があります。")
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
    key = derive_key(password, salt, mode='dec', file=input_path)

    try:
        cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    except Exception as e:
        print(f"[!] パスワードが間違っているか、ファイルが破損しています。ファイル '{input_path}' は復号できません。")
        return  # パスワードが間違っている場合は復号せずスキップ
    
    temp_output_path = "temp_decrypted_output.pdf"
    with open(temp_output_path, "wb") as f:
        f.write(decrypted_data)

    if not is_valid_pdf(temp_output_path):
        os.remove(temp_output_path)  # 検証用ファイルを削除
        print("[!] 復号したファイルはPDF形式ではありません。整合性が取れていません。")
        return

    # 5. 出力ファイルに保存
    if not output_path:
        base = os.path.splitext(input_path)[0]
        output_path = base + ".pdf"
    else:
        base = os.path.splitext(output_path)[0]
        output_path = base + ".pdf"
    
    os.remove(temp_output_path)  # 一時ファイルを削除
    
    if os.path.exists(output_path) and not force:
        print(f"[!] 出力先ファイル '{output_path}' は既に存在します。--force を指定して上書きできます。")
        return

    with open(output_path, "wb") as f:
        f.write(decrypted_data)

    print(f"[+] Decrypted and saved to: {output_path}")