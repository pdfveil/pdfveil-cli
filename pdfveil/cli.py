# pdfveil/cli.py
import argparse
import getpass
from .encryptor import encrypt_pdf
from .decryptor import decrypt_pdf
from . import __version__
from .logo import ASCII_LOGO

def run_cli():
    parser = argparse.ArgumentParser(
        prog="pdfveil",
        description="🔐 PDFをAES-GCMで安全に暗号化・復号するCLIツール",
    )
    
    # --version フラグ
    parser.add_argument("--version", action="store_true", help="バージョン情報を表示")
    
    # 一旦 version だけ拾う
    args, remaining_args = parser.parse_known_args()
    if args.version:
        print(ASCII_LOGO)
        print(f"Version: {__version__}")
        return

    subparsers = parser.add_subparsers(dest="command", required=True)

    # 暗号化コマンド
    encrypt_parser = subparsers.add_parser("encrypt", aliases=["enc"], help="PDFを暗号化する")
    encrypt_parser.add_argument("inputpdf", help="入力PDFファイルパス")
    encrypt_parser.add_argument("-p" ,"--password", help="暗号化に使うパスワード")
    encrypt_parser.add_argument("-o" ,"--output", help="保存先ファイル名（省略時: .veil.pdf）")
    encrypt_parser.add_argument("-f", "--force", action="store_true", help="既存ファイルを強制上書きする")

    # 復号コマンド
    decrypt_parser = subparsers.add_parser("decrypt", aliases=["dec"], help="PDFを復号する")
    decrypt_parser.add_argument("veilpdf", help="暗号化されたファイル（.veil.pdf）")
    decrypt_parser.add_argument("-p", "--password", help="復号に使うパスワード")
    decrypt_parser.add_argument("-o" ,"--output", help="保存先ファイル名（省略時: .decrypted.pdf）")
    decrypt_parser.add_argument("-f", "--force", action="store_true", help="既存ファイルを強制上書きする")

    args = parser.parse_args()
    
    # --version フラグがあれば表示して終了
    if args.version:
        print(ASCII_LOGO)
        print(f"📦 Version: {__version__}")
        return
    
    # 対話式パスワード入力（-pが省略されたら）
    if not args.password:
        args.password = getpass.getpass("🔑 Enter password: ")

    # サブコマンド実行
    if args.command in ["encrypt", "enc"]:
        encrypt_pdf(args.inputpdf, args.password, args.output, args.force)
    elif args.command in ["decrypt", "dec"]:
        decrypt_pdf(args.veilpdf, args.password, args.output, args.force)