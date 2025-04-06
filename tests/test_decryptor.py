# tests/test_decryptor.py
import os
import hashlib
from pypdf import PdfReader
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
    
# PDFファイルのハッシュ値を取得する関数        
def get_file_hash(file_path: str) -> str:
    """ファイルのSHA256ハッシュを取得"""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# PDFからテキストを抽出する関数
def extract_text_from_pdf(file_path: str) -> str:
    """PDFからテキストを抽出"""
    with open(file_path, "rb") as f:
        reader = PdfReader(f)  # PdfReaderのインスタンス作成
        text = ""
        for page in reader.pages:
            text += page.extract_text()  # 各ページからテキストを抽出
    return text

def test_decrypt_pdf_success():
    # 復号
    decrypt_pdf(ENCRYPTED_FILE, PASSWORD, output_path=DECRYPTED_FILE, force=True)

    # ハッシュ値の比較
    original_hash = get_file_hash(TEST_PDF)
    decrypted_hash = get_file_hash(DECRYPTED_FILE)
    assert original_hash == decrypted_hash, "The hash of the decrypted PDF does not match the original PDF."

    # テキストの比較
    original_text = extract_text_from_pdf(TEST_PDF)
    decrypted_text = extract_text_from_pdf(DECRYPTED_FILE)
    assert original_text == decrypted_text, "The decrypted PDF content does not match the original PDF content."
