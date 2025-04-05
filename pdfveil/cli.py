# pdfveil/cli.py
import argparse
import getpass
import glob
import os
from colorama import init, Fore
from .encryptor import encrypt_pdf
from .decryptor import decrypt_pdf
from . import __version__
from .logo import ASCII_LOGO

# 初期化
init(autoreset=True)

def process_files_one_by_one(files, mode, force, passwords, remove=False, output=None):
    # パスワードリストをファイル数分用意し、1つずつ処理する
    for idx, file in enumerate(files):
        password = passwords[idx]  # 既にリストでパスワードを取得しているため、ここではリストから取得
        if not password:
            print("[!] 暗号化にはパスワードが必要です。")
            exit(1)

        # ファイルが存在するかチェック
        matched_files = glob.glob(file)
        if not matched_files:
            print(f"[!] 指定されたファイル '{file}' が見つかりません。")
            continue
        
        try:
            # 暗号化処理
            if mode == 'encrypt' or mode == 'enc':
                encrypt_pdf(matched_files[0], password, output_path=output, force=force)
                if remove:
                    os.remove(matched_files[0])
                    print(f"[i] 元のPDF '{matched_files[0]}' を削除しました。")
        
            # 復号処理
            elif mode == 'decrypt' or mode == 'dec':
                decrypt_pdf(matched_files[0], password, output_path=output, force=force)
                if remove:
                    os.remove(matched_files[0])
                    print(f"[i] 元のPDF '{matched_files[0]}' を削除しました。")
        except Exception as e:
            print(f"[!] エラー: {e}")
            continue

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
    encrypt_parser.add_argument("inputpdf", help=Fore.YELLOW + "入力PDFファイルパス (複数指定可能、ワイルドカードも対応)" + Fore.RESET, nargs='+')
    encrypt_parser.add_argument("-p" ,"--password", help=Fore.YELLOW + "暗号化に使うパスワード（1つ指定で共通、複数指定で個別対応）" + Fore.RESET, nargs='+')
    encrypt_parser.add_argument("-o" ,"--output", help=Fore.YELLOW + "保存先ファイル名（省略時: .veil.pdf）" + Fore.RESET)
    encrypt_parser.add_argument("-f", "--force", action="store_true", help=Fore.YELLOW + "既存ファイルを強制上書きする" + Fore.RESET)
    encrypt_parser.add_argument("--remove", action="store_true", help=Fore.YELLOW + "暗号化後に元のPDFを削除する" + Fore.RESET)

    # 復号コマンド
    decrypt_parser = subparsers.add_parser("decrypt", aliases=["dec"], help=Fore.YELLOW + "PDFを復号する" + Fore.RESET)
    decrypt_parser.add_argument("veilpdf", help=Fore.YELLOW + "暗号化されたファイル（.veil.pdf）" + Fore.RESET, nargs='+')
    decrypt_parser.add_argument("-p", "--password", help=Fore.YELLOW + "復号に使うパスワード（1つ指定で共通、複数指定で個別対応）" + Fore.RESET, nargs='+')
    decrypt_parser.add_argument("-o" ,"--output", help=Fore.YELLOW + "保存先ファイル名（省略時: .decrypted.pdf）" + Fore.RESET)
    decrypt_parser.add_argument("-f", "--force", action="store_true", help=Fore.YELLOW + "既存ファイルを強制上書きする" + Fore.RESET)
    decrypt_parser.add_argument("--remove", action="store_true", help=Fore.YELLOW + "復号後に .veil ファイルを削除する" + Fore.RESET)

    
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

    # ワイルドカードによる複数ファイルを処理
    all_files = []
    for file in args.inputpdf if args.command in ["encrypt", "enc"] else args.veilpdf:
        all_files.extend(glob.glob(file))
    
    if not all_files:
        print(f"[!] 指定されたファイルが見つかりません。")
        exit(1)
    
    # パスワード処理
    passwords = []
    if args.password:
        if len(args.password) == 1:
            # 一つさけ指定 -> 全ファイルに共有パスワード
            passwords = args.password * len(all_files)
        elif len(args.password) == len(all_files):
            # ファイル数と一致 -> 個別パスワード
            passwords = args.password
        else:
            print(f"[!] エラー: パスワードの数 ({len(args.password)}) がファイル数 ({len(all_files)}) と一致しません。")
            exit(1)
    else:
        # パスワード未指定 -> ユーザーから入力
        for file in all_files:
            password = getpass.getpass(f"🔑 Enter password for {file}: ")
            if not password:
                print("[!] パスワードが必要です。")
                exit(1)
            passwords.append(password)
   
    
    # サブコマンド実行
    if args.command in ["encrypt", "enc"]:
        process_files_one_by_one(all_files, "encrypt", args.force, passwords, remove=args.remove, output=args.output)
    elif args.command in ["decrypt", "dec"]:
        process_files_one_by_one(all_files, "decrypt", args.force, passwords, remove=args.remove, output=args.output)
