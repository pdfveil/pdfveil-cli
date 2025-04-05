# tests/test_decryptor.py
import os
import hashlib
from pdfveil.encryptor import encrypt_pdf
from pdfveil.decryptor import decrypt_pdf

TEST_PDF = "tests/test_files/sample.pdf"
ENCRYPTED_FILE = "tests/test_files/sample.veil"
DECRYPTED_FILE = "tests/test_files/sample_decrypted.pdf"
PASSWORD = "testpassword"

def setup_module(module):
    # 暗号化して .veil を用意
    encrypt_pdf(TEST_PDF, PASSWORD, output_path=ENCRYPTED_FILE, force=True, skip_strength_check=True)

def teardown_module(module):
    # テスト後のクリーンアップ
    for f in [ENCRYPTED_FILE, DECRYPTED_FILE]:
        if os.path.exists(f):
            os.remove(f)
            
def get_file_hash(file_path: str) -> str:
    """ファイルのSHA256ハッシュを取得"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def test_decrypt_pdf_success():
    # 復号
    decrypt_pdf(ENCRYPTED_FILE, PASSWORD, output_path=DECRYPTED_FILE, force=True)

    # 元PDFと一致するか
    with open(TEST_PDF, "rb") as f1, open(DECRYPTED_FILE, "rb") as f2:
        # ハッシュ値を比較して検証
        original_hash = get_file_hash(TEST_PDF)
        decrypted_hash = get_file_hash(DECRYPTED_FILE)
        assert original_hash == decrypted_hash, "The decrypted file does not match the original file."