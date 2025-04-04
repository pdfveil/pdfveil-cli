# pdfveil/cli.py
import argparse
from .encryptor import encrypt_pdf
from .decryptor import decrypt_pdf

def run_cli():
    parser = argparse.ArgumentParser(
        prog="pdfveil",
        description="🔐 PDFをAES-GCMで安全に暗号化・復号するCLIツール",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # 暗号化コマンド
    encrypt_parser = subparsers.add_parser("encrypt", aliases=["enc"], help="PDFを暗号化する")
    encrypt_parser.add_argument("inputpdf", help="入力PDFファイルパス")
    encrypt_parser.add_argument("-p" ,"--password", required=True, help="暗号化に使うパスワード")
    encrypt_parser.add_argument("-o" ,"--output", help="保存先ファイル名（省略時: .veil.pdf）")

    # 復号コマンド
    decrypt_parser = subparsers.add_parser("decrypt", aliases=["enc"], help="PDFを復号する")
    decrypt_parser.add_argument("veilpdf", help="暗号化されたファイル（.veil.pdf）")
    decrypt_parser.add_argument("-p", "--password", required=True, help="復号に使うパスワード")
    decrypt_parser.add_argument("-o" ,"--output", help="保存先ファイル名（省略時: .decrypted.pdf）")

    args = parser.parse_args()

    # サブコマンド実行
    if args.command == "encrypt":
        encrypt_pdf(args.input, args.password, args.output)
    elif args.command == "decrypt":
        decrypt_pdf(args.input, args.password, args.output)