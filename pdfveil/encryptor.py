# pdfveil/encryptor.py
import os
import struct
import hmac
import hashlib
from pypdf import PdfReader, PdfWriter
from pypdf.generic import IndirectObject
from io import BytesIO
from .utils import generate_salt, derive_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

def extract_info_object_source(reader: PdfReader, info_ref: IndirectObject) -> bytes:
    # raw_source は PdfReader._get_object() などから間接的に取得可能
    obj_id = info_ref.idnum
    obj_gen = info_ref.generation
    obj = reader.get_object(info_ref)

    # /Infoの辞書内容を構築
    content_lines = [f"{obj_id} {obj_gen} obj", "<<"]
    for key, value in obj.items():
        content_lines.append(f"{key} ({value})")
    content_lines.append(">>\nendobj\n")

    return "\n".join(content_lines).encode("utf-8")

def extract_pdf_metadata(file_path: str) -> bytes:
    """PDFのヘッダーとメタデータ部分をバイナリで取り出す"""
    
    # 1. ヘッダーだけ先に取得
    with open(file_path, "rb") as f:
        header = f.readline().decode("utf-8", errors="ignore").strip()
        header_bytes = (header + "\n").encode("utf-8")

    # 2. PdfReaderにパスを直接渡す（内部で開いてくれる）
    reader = PdfReader(file_path)

    # 3. Infoオブジェクトを取得
    info_ref = reader.trailer.get("/Info")
    if not info_ref:
        raise ValueError("このPDFには/Infoオブジェクトが存在しません")

    metadata_obj = extract_info_object_source(reader, info_ref)

    # 任意：中身を保存して確認したいなら
    with open("metadata.txt", "wb") as metadata_file:
        metadata_file.write(header_bytes + metadata_obj)

    return header_bytes + metadata_obj

def extract_body_without_metadata(input_path: str) -> bytes:
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)
    
    # trailer から /Info を削除（書き出し時に無視される）
    if "/Info" in reader.trailer:
        del reader.trailer["/Info"]

    # メタデータを明示的に空にする
    writer.add_metadata({})
    if hasattr(writer, "_info"):
        writer._info = None  # 強制的にInfo参照を消す

    

    # メモリ上で保存
    buffer = BytesIO()
    writer.write(buffer)
    body_data =  buffer.getvalue()
    
    modified_pdf_data = body_data
    
    return modified_pdf_data

def encrypt_pdf(input_path: str, password: str, output_path: str = None, force: bool = False, skip_strength_check=False, encrypt_metadata=True):
    """PDFファイルをAES-GCMで暗号化し、.veilとして保存"""
    
    if not input_path.lower().endswith(".pdf"):
        raise ValueError(f"[!] 入力ファイルはPDF (.pdf) 形式である必要があります。")
    
    # 1. PDFを読み込み
    with open(input_path, "rb") as f:
        body_data = extract_body_without_metadata(input_path)
        meta_data = extract_pdf_metadata(input_path)

    # 2. ソルト & 鍵生成
    body_salt = generate_salt()
    meta_salt = generate_salt()
    body_key = derive_key(password, body_salt, mode='enc', file=input_path, skip_strength_check=skip_strength_check)
    meta_key = derive_key(password, meta_salt, mode='enc', file=input_path, skip_strength_check=skip_strength_check)

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
        cipher_for_metadata = Cipher(algorithms.AES(meta_key), modes.GCM(metadata_iv))
        encryptor_meta = cipher_for_metadata.encryptor()
        metadata_ciphertext = encryptor_meta.update(meta_data) + encryptor_meta.finalize()
        metadata_tag = encryptor_meta.tag
        metadata_length = len(metadata_ciphertext) # メタデータのバイト長
        packed_length = struct.pack(">I", metadata_length) # 4バイト符号なし整数(ビッグエンディアン)
        
    # 5. AES-GCMで暗号化
    cipher = Cipher(algorithms.AES(body_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(body_data) + encryptor.finalize()
    tag = encryptor.tag  # 認証タグ（16バイト）

    # 6. 暗号化ファイルに [salt][iv][metadata][ciphertext][tag] を保存
    if input_path.lower().endswith(".pdf"):
        base = input_path[:-4]
    else:
        base = os.path.splitext(input_path)[0]
    output_path = base + ".veil"

    
    if os.path.exists(output_path) and not force:
        raise ValueError(f"[!] 出力先ファイル '{output_path}' は既に存在します。--force を指定して上書きできます。")

    with open(output_path, "wb") as f:
        # [magic(4)][flag(1)][meta_length(4)][metadata_raw(?)][salt(16)][iv(12)][cipher_length(4)][ciphertext(?)][tag(16)]
        f.write(b"VEIL")  # Add VEIl marker
        f.write(b"\x01")  # Add Version marker
        f.write(flag)
        if encrypt_metadata:
            #[magic(4)][flag(1)][meta_salt(16)][meta_iv(12)][meta_length(4)][metadata_ciphertext(?)][meta_tag(16)][salt(16)][iv(12)][cipher_length(4)][ciphertext(?)][tag(16)]
            f.write(meta_salt)
            f.write(metadata_iv)
            f.write(packed_length)
            f.write(metadata_ciphertext)
            f.write(metadata_tag)
        else:
            f.write(meta_salt)
            meta_length = len(meta_data)
            f.write(struct.pack(">I", meta_length))
            f.write(meta_data)
            
            # HMACを使って整合性チェック用タグを生成（meta_keyでHMAC）
            hmac_tag = hmac.new(meta_key, meta_data, hashlib.sha256).digest()
            f.write(hmac_tag)  # 長さは32バイト
        f.write(body_salt)
        f.write(iv)
        cipher_length = len(ciphertext)
        data_packed_length = struct.pack(">I", cipher_length)
        f.write(data_packed_length)
        f.write(ciphertext)
        f.write(tag)


    print(f"[+] Encrypted and saved to: {output_path}")

"""
.veil file format (version 1):
[magic(4)="VEIL"][version(1)][flag(1)]
    if flag==0x01:
        [meta_salt(16)][meta_iv(12)][meta_len(4)][meta_ciphertext(?)][meta_tag(16)]
    else:
        [meta_salt(16)][meta_len(4)][meta_plaintext(?)][meta_hmac(32)]
    [body_salt(16)][iv(12)][cipher_len(4)][ciphertext(?)][tag(16)]
"""
