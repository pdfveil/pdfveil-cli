# pdfveil/encryptor.py
import os
import sys
import struct
from pypdf import PdfReader
from .utils import generate_salt, derive_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def extract_pdf_metadata(file_path: str) -> bytes:
    """pypdfを使用してPDFのメタデータを抽出してバイト列に変換"""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)
        metadata = reader.metadata  # メタデータを取得
    metadata_str = str(metadata).encode("utf-8")  # メタデータを文字列としてエンコード
    return metadata_str

def encrypt_pdf(input_path: str, password: str, output_path: str = None, force: bool = False, skip_strength_check=False, encrypt_metadata=True):
    """PDFファイルをAES-GCMで暗号化し、.veilとして保存"""
    
    if not input_path.lower().endswith(".pdf"):
        print(f"[!] 入力ファイルはPDF (.pdf) 形式である必要があります。")
        sys.exit(1)
    
    # 1. PDFを読み込み
    with open(input_path, "rb") as f:
        data = f.read()

    # 2. ソルト & 鍵生成
    salt = generate_salt()
    key = derive_key(password, salt, mode='enc', file=input_path, skip_strength_check=skip_strength_check)

    # 3. IV生成（GCM推奨：12バイト）
    metadata_iv = b""
    iv = os.urandom(12)  # AES-GCMではIVは12バイトが推奨されている
    
    # 1バイトのフラグをセット（0x01: メタデータあり, 0x00: メタデータなし）
    flag = b'\x01' if encrypt_metadata else b'\x00'
    
    # 4. メタデータの暗号化
    metadata_ciphertext = b""
    metadata_tag = b""  # 最初に初期化しておく 
    if encrypt_metadata:
        metadata_iv = os.urandom(12)  # メタデータ用のIVも生成
        metadata = extract_pdf_metadata(input_path)
        cipher_for_metadata = Cipher(algorithms.AES(key), modes.GCM(metadata_iv))
        encryptor_meta = cipher_for_metadata.encryptor()
        metadata_ciphertext = encryptor_meta.update(metadata) + encryptor_meta.finalize()
        metadata_tag = encryptor_meta.tag
        metadata_length = len(metadata_ciphertext) # メタデータのバイト長
        packed_length = struct.pack(">I", metadata_length) # 4バイト符号なし整数(ビッグエンディアン)
        
    # 5. AES-GCMで暗号化
    cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(data) + encryptor.finalize()
    tag = encryptor.tag  # 認証タグ（16バイト）

    # 6. 暗号化ファイルに [salt][iv][metadata][ciphertext][tag] を保存
    if not output_path:
        output_path = input_path.replace(".pdf", ".veil")
    else:
        # 強制的に .veil 拡張子にする
        base = os.path.splitext(output_path)[0]
        output_path = base + ".veil"

    
    if os.path.exists(output_path) and not force:
        print(f"[!] 出力先ファイル '{output_path}' は既に存在します。--force を指定して上書きできます。")
        return

    with open(output_path, "wb") as f:
        f.write(flag)
        f.write(salt)
        if encrypt_metadata:
            #[flag(1)][salt(16)][metadata_iv(12)][metadata_length(4)][metadata_ciphertext(?)][metadata_tag(16)][iv(12)][ciphertext(?)][tag(16)]

            f.write(metadata_iv)
            f.write(packed_length)
            f.write(metadata_ciphertext)
            f.write(metadata_tag)
        f.write(iv)
        f.write(ciphertext)
        f.write(tag)


    print(f"[+] Encrypted and saved to: {output_path}")