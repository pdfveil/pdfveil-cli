# pdfveil/cli.py
import argparse
import getpass
from colorama import init, Fore
from .encryptor import encrypt_pdf
from .decryptor import decrypt_pdf
from . import __version__
from .logo import ASCII_LOGO

# 初期化
init(autoreset=True)

def run_cli():
    # ArgumentParserの設定
    parser = argparse.ArgumentParser(
        prog="pdfveil",
        description=Fore.CYAN + "🔐 PDFをAES-GCMで安全に暗号化・復号するCLIツール" + Fore.RESET,
        formatter_class=argparse.RawTextHelpFormatter,  # より読みやすいヘルプ表示
    )
    
    # --version フラグ
    parser.add_argument("--version", action="store_true", help=Fore.GREEN + "バージョン情報を表示" + Fore.RESET)
    
    # サブコマンドの設定
    subparsers = parser.add_subparsers(dest="command", required=True)

    # 暗号化コマンド
    encrypt_parser = subparsers.add_parser("encrypt", aliases=["enc"], help=Fore.YELLOW + "PDFを暗号化する" + Fore.RESET)
    encrypt_parser.add_argument("inputpdf", help=Fore.YELLOW + "入力PDFファイルパス" + Fore.RESET)
    encrypt_parser.add_argument("-p" ,"--password", help=Fore.YELLOW + "暗号化に使うパスワード" + Fore.RESET)
    encrypt_parser.add_argument("-o" ,"--output", help=Fore.YELLOW + "保存先ファイル名（省略時: .veil.pdf）" + Fore.RESET)
    encrypt_parser.add_argument("-f", "--force", action="store_true", help=Fore.YELLOW + "既存ファイルを強制上書きする" + Fore.RESET)

    # 復号コマンド
    decrypt_parser = subparsers.add_parser("decrypt", aliases=["dec"], help=Fore.YELLOW + "PDFを復号する" + Fore.RESET)
    decrypt_parser.add_argument("veilpdf", help=Fore.YELLOW + "暗号化されたファイル（.veil.pdf）" + Fore.RESET)
    decrypt_parser.add_argument("-p", "--password", help=Fore.YELLOW + "復号に使うパスワード" + Fore.RESET)
    decrypt_parser.add_argument("-o" ,"--output", help=Fore.YELLOW + "保存先ファイル名（省略時: .decrypted.pdf）" + Fore.RESET)
    decrypt_parser.add_argument("-f", "--force", action="store_true", help=Fore.YELLOW + "既存ファイルを強制上書きする" + Fore.RESET)

    
    # 最初に引数を解析
    args = parser.parse_args()

    # --version フラグがあれば表示して終了
    if args.version:
        print(ASCII_LOGO)
        print(f"📦 Version: {__version__}")
        return
        
    # コマンドが指定されていない場合はエラーメッセージを表示
    if not args.command:
        print("[!] エラー: コマンドが不足しています。コマンドを指定してください。")
        print("使用方法:")
        print("  python main.py encrypt <入力PDFファイル> --password <パスワード>")
        print("  python main.py decrypt <暗号化されたファイル> --password <パスワード>")
        exit(1)

    # 対話式パスワード入力（-pが省略されたら）
    if not args.password:
        args.password = getpass.getpass("🔑 Enter password: ")

    # サブコマンド実行
    if args.command in ["encrypt", "enc"]:
        encrypt_pdf(args.inputpdf, args.password, args.output, args.force)
    elif args.command in ["decrypt", "dec"]:
        decrypt_pdf(args.veilpdf, args.password, args.output, args.force)