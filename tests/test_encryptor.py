import os
import pytest
from pdfveil.encryptor import encrypt_pdf

TEST_DIR = os.path.dirname(__file__)
TEST_PDF = os.path.join(TEST_DIR, "test_files/sample.pdf")
TEST_TXT = os.path.join(TEST_DIR, "test_files/sample.txt")
OUT_FILE = os.path.join(TEST_DIR, "output.veil")

def teardown_module(module):
    # テスト後に出力ファイルを消す
    if os.path.exists(OUT_FILE):
        os.remove(OUT_FILE)

def test_encrypt_pdf_success():
    encrypt_pdf(TEST_PDF, "testpassword", output_path=OUT_FILE, force=True)
    assert os.path.exists(OUT_FILE)
    assert os.path.getsize(OUT_FILE) > 0

def test_encrypt_pdf_existing_file_no_force():
    # 先にファイル作っておく
    with open(OUT_FILE, "wb") as f:
        f.write(b"dummy")

    # force=False のときに上書きされないことを確認
    encrypt_pdf(TEST_PDF, "testpassword", output_path=OUT_FILE, force=False)
    with open(OUT_FILE, "rb") as f:
        content = f.read()
    assert content == b"dummy"  # 中身が変わっていない

def test_encrypt_pdf_wrong_input_type():
    with pytest.raises(SystemExit):
        encrypt_pdf(TEST_TXT, "testpassword", output_path=OUT_FILE)

def test_encrypt_pdf_default_output_path(tmp_path):
    # .veilが自動でつくか
    test_pdf = tmp_path / "test.pdf"
    test_pdf.write_bytes(b"%PDF-1.4 sample data")
    encrypt_pdf(str(test_pdf), "pass123")
    output_path = str(test_pdf).replace(".pdf", ".veil")
    assert os.path.exists(output_path)