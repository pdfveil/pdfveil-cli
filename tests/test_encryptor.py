import os
import pytest
import json
from pypdf import PdfWriter
from pdfveil.encryptor import encrypt_pdf, extract_pdf_metadata

TEST_DIR = os.path.dirname(__file__)
TEST_PDF = os.path.join(TEST_DIR, "test_files/sample.pdf")
TEST_TXT = os.path.join(TEST_DIR, "test_files/sample.txt")
OUT_FILE = os.path.join(TEST_DIR, "output.veil")

def teardown_module(module):
    # テスト後に出力ファイルを消す
    if os.path.exists(OUT_FILE):
        os.remove(OUT_FILE)


def test_encrypt_pdf_success():
    encrypt_pdf(TEST_PDF, "testpassword", output_path=OUT_FILE, force=True, skip_strength_check=True)
    assert os.path.exists(OUT_FILE)
    assert os.path.getsize(OUT_FILE) > 0

def test_encrypt_pdf_existing_file_no_force():
    # 先にファイル作っておく
    with open(OUT_FILE, "wb") as f:
        f.write(b"dummy")

    # force=False のときに上書きされないことを確認
    encrypt_pdf(TEST_PDF, "testpassword", output_path=OUT_FILE, force=False, skip_strength_check=True)
    with open(OUT_FILE, "rb") as f:
        content = f.read()
    assert content == b"dummy"  # 中身が変わっていない

def test_encrypt_pdf_wrong_input_type():
    with pytest.raises(SystemExit):
        encrypt_pdf(TEST_TXT, "testpassword", output_path=OUT_FILE)

def test_encrypt_pdf_default_output_path(tmp_path):
    # .veilが自動でつくか
    test_pdf = tmp_path / "test.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    with open(test_pdf, "wb") as f:
        writer.write(f)

    # テスト対象呼び出し
    encrypt_pdf(str(test_pdf), "pass123", skip_strength_check=True)

    output_path = str(test_pdf).replace(".pdf", ".veil")
    assert os.path.exists(output_path)
    
def test_extract_pdf_metadata_returns_json():
    test_pdf = os.path.join(os.path.dirname(__file__), "test_files/sample.pdf")
    
    metadata_bytes = extract_pdf_metadata(test_pdf)

    # 1. 型チェック
    assert isinstance(metadata_bytes, bytes)

    # 2. JSONにデコードできるか
    try:
        metadata_dict = json.loads(metadata_bytes.decode("utf-8"))
    except json.JSONDecodeError:
        assert False, "抽出されたメタデータはJSON形式ではありません"

    # 3. キーとバリューが文字列であることを確認
    assert all(isinstance(k, str) for k in metadata_dict.keys())
    assert all(isinstance(v, str) for v in metadata_dict.values())

    # 4. 代表的なメタデータ項目が存在するかチェック（例: ProducerやCreator）
    expected_keys = ["/Producer", "/Creator", "/CreationDate"]
    assert any(k in metadata_dict for k in expected_keys)
