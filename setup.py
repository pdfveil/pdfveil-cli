from setuptools import setup, find_packages

setup(
    name="pdfveil",
    version="0.1.0",
    description="A CLI tool for encrypting and decrypting PDF files",
    author="Saku0512",
    author_email="comonraven113@gmail.com",
    packages=find_packages(),  # パッケージディレクトリを自動検出
    entry_points={
        "console_scripts": [
            "pdfveil=pdfveil.cli:main",  # CLIエントリポイント
        ],
    },
)