# pdfveil/decryptor.py
# encrypted metadata false
# [salt(16)][iv(12)][ciphertext(?)][tag(16)]
# encrypted metadata true
# [flag(1)][salt(16)][metadata_iv(12)][metadata_ciphertext][metadata_tag(16)][iv(12)][ciphertext][tag(16)]
from .utils import derive_key
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import sys
import os
import struct
import re
from datetime import datetime, timedelta

def parse_pdf_date(pdf_date_str: str) -> str:
    """PDF日付文字列（例: D:20250404160638+00'00'）を整形"""
    match = re.match(r"D:(\d{4})(\d{2})(\d{2})(\d{2})(\d{2})(\d{2})([+-Z])?(\d{2})?'?(\d{2})?'?", pdf_date_str)
    if not match:
        return pdf_date_str  # フォーマット不明ならそのまま

    year, month, day, hour, minute, second, tz_sign, tz_hour, tz_minute = match.groups()
    dt = datetime(int(year), int(month), int(day), int(hour), int(minute), int(second))

    # タイムゾーンの調整（現状は JST 固定にする）
    jst = dt + timedelta(hours=9)
    return jst.strftime("%a %b %d %H:%M:%S %Y JST")

def print_formatted_metadata(meta_dict: dict):
    """整形してメタデータを出力"""
    print("[*] Metadata")
    for key in sorted(meta_dict.keys()):
        clean_key = key.strip("/")

        value = meta_dict[key]
        if "Date" in clean_key and isinstance(value, str):
            value = parse_pdf_date(value)

        print(f"{clean_key+':':<16}{value}")
    print("\n")

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
    
    offset = 0
    
    # 2. フラグを読み取り
    flag = encrypted_data[offset]
    offset += 1
    
    # 3. ソルトを抽出
    salt = encrypted_data[offset:offset+16]
    offset += 16

    # 3. 鍵を導出
    key = derive_key(password, salt, mode='dec', file=input_path)

    try:
        if flag == 0x00:
            # メタデータなし構造: [flag][salt][iv][ciphertext][tag]
            iv = encrypted_data[offset:offset+12]
            offset += 12
            tag = encrypted_data[-16:]
            ciphertext = encrypted_data[offset:-16]
        elif flag == 0x01:
            # メタデータあり構造
            # [flag][salt][metadata_iv][metadata_length][metadata_ciphertext][metadata_tag][iv][ciphertext][tag]
            metadata_iv = encrypted_data[offset:offset+12]
            offset += 12
            
            # メタデータの長さが不明なので、末尾の[iv+ciphertext][tag(16)]を逆から読む
            # -> tag(16) + iv(12)は固定 -> 残りがmetadata_ciphertxt ; metadata_tag
            metadata_len = struct.unpack(">I", encrypted_data[offset:offset+4])[0]
            offset += 4
            
            metadata_ciphertext = encrypted_data[offset:offset+ metadata_len]
            offset += metadata_len
            
            metadata_tag = encrypted_data[offset:offset+16]
            offset += 16
            
            # メタデータ復号(今は表示だけ。利用しない)
            cipher_meta = Cipher(algorithms.AES(key), modes.GCM(metadata_iv, metadata_tag))
            decryptor_meta = cipher_meta.decryptor()
            try:
                metadata_plan = decryptor_meta.update(metadata_ciphertext) + decryptor_meta.finalize()
                meta_dict = eval(metadata_plan.decode('utf-8'))  # ※将来的に安全にするならJSONにした方がよい
                print_formatted_metadata(meta_dict)
            except Exception as e:
                print(f"[!] メタデータの復号に失敗しました: {e}")
                return
        else:
            print("[!] 不明なフラグです。ファイルが破損している可能性があります。")
            return

        iv = encrypted_data[offset:offset+12]
        offset += 12
        tag = encrypted_data[-16:]
        ciphertext = encrypted_data[offset:-16]
        try:
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
        except Exception as e:
            print(f"[!] 復号に失敗しました。パスワードが間違っているか、ファイルが破損している可能性があります。")
            return
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