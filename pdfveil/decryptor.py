import os
import struct
import sys
import hmac
import hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from .utils import derive_key
from io import BytesIO
from pypdf import PdfReader, PdfWriter

def decrypt_pdf(input_path: str, password: str, output_path: str = None, force: bool = False, skip_strength_check=False):
    with open(input_path, "rb") as f:
        magic = f.read(4)
        if magic != b"VEIL":
            raise ValueError("無効なVEILファイル: magicヘッダーが見つかりません")
        
        version = f.read(1)
        if version != b"\x01":
            raise ValueError(f"未対応のバージョン: {version.hex()}")

        flag = f.read(1)

        encrypt_metadata = flag == b'\x01'

        # --- メタデータ処理 ---
        meta_data = b""
        if encrypt_metadata:
            meta_salt = f.read(16)
            metadata_iv = f.read(12)
            metadata_len = struct.unpack(">I", f.read(4))[0]
            metadata_ciphertext = f.read(metadata_len)
            metadata_tag = f.read(16)
            meta_key = derive_key(password, meta_salt, mode='dec', file=input_path, skip_strength_check=skip_strength_check)

            cipher = Cipher(algorithms.AES(meta_key), modes.GCM(metadata_iv, metadata_tag))
            decryptor = cipher.decryptor()
            meta_data = decryptor.update(metadata_ciphertext) + decryptor.finalize()

        else:
            meta_salt = f.read(16)
            metadata_len = struct.unpack(">I", f.read(4))[0]
            meta_data = f.read(metadata_len)
            hmac_tag = f.read(32)
            meta_key = derive_key(password, meta_salt, mode='dec', file=input_path, skip_strength_check=skip_strength_check)
            expected_tag = hmac.new(meta_key, meta_data, hashlib.sha256).digest()
            if not hmac.compare_digest(hmac_tag, expected_tag):
                raise ValueError("メタデータのHMAC検証に失敗しました。パスワードが間違っている可能性があります。")

        # --- 本体データ処理 ---
        body_salt = f.read(16)
        iv = f.read(12)
        cipher_len = struct.unpack(">I", f.read(4))[0]
        ciphertext = f.read(cipher_len)
        tag = f.read(16)

        body_key = derive_key(password, body_salt, mode='dec', file=input_path, skip_strength_check=skip_strength_check)
        cipher = Cipher(algorithms.AES(body_key), modes.GCM(iv, tag))
        decryptor = cipher.decryptor()
        pdf_body = decryptor.update(ciphertext) + decryptor.finalize()

    # --- 出力ファイル名決定 ---
    if not output_path:
        base = os.path.splitext(input_path)[0]
        output_path = base + ".pdf"

    if os.path.exists(output_path) and not force:
        raise ValueError(f"[!] 出力ファイル '{output_path}' は既に存在します。--force を指定して上書きできます。")

    # --- PDFの再構築 ---
    # 1. ボディをPDFとしてロード
    body_reader = PdfReader(BytesIO(pdf_body))
    writer = PdfWriter()

    for page in body_reader.pages:
        writer.add_page(page)

    # 2. メタデータ再追加
    if encrypt_metadata:
        # 暗号化されていた場合 -> ヘッダーとInfoオブジェクトを復元
        with open(output_path, "wb") as f:
            f.write(meta_data)
            buffer = BytesIO()
            writer.write(buffer)
            f.write(buffer.getvalue())
    else:
        # 平文で含まれていた場合 -> PdfWriter のAPIで設定
        from pypdf.generic import NameObject, create_string_object
        try:
            header_end = meta_data.index(b"\n<<")
            meta_dict_raw = meta_data[header_end+1:-len(">>\nendobj\n")]
            lines = meta_dict_raw.split(b"\n")
            info_dict = {}
            for line in lines:
                if b"(" in line and b")" in line:
                    key, val = line.split(b"(", 1)
                    key = key.strip().decode("utf-8")
                    val = val.rstrip(b")").decode("utf-8")
                    info_dict[NameObject(key)] = create_string_object(val)

            writer.add_metadata(info_dict)
        except Exception as e:
            print(f"[!] メタデータの解析に失敗しましたが、PDF本体は復元できます: {e}")

        with open(output_path, "wb") as f:
            writer.write(f)

    print(f"[+] Decrypted and saved to: {output_path}")