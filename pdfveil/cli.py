import argparse
from .encryptor import encrypt_pdf
from .decryptor import decrypt_pdf

def run_cli():
    parser = argparse.ArgumentParser(prog="pdfveil", description="Encrypt or decrypt PDF files with strong AES-GCM encryption.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # encryptコマンド
    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a PDF file")
    encrypt_parser.add_argument("input", help="Input PDF file")
    encrypt_parser.add_argument("--password", "-p", required=True, help="Password for encryption")
    encrypt_parser.add_argument("--output", "-o", help="Output encrypted file path")

    # decryptコマンド
    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a .veil.pdf file")
    decrypt_parser.add_argument("input", help="Encrypted .veil.pdf file")
    decrypt_parser.add_argument("--password", "-p", required=True, help="Password for decryption")
    decrypt_parser.add_argument("--output", "-o", help="Output decrypted PDF path")

    args = parser.parse_args()

    if args.command == "encrypt":
        encrypt_pdf(args.input, args.password, args.output)
    elif args.command == "decrypt":
        decrypt_pdf(args.input, args.password, args.output)