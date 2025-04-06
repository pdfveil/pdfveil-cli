![Build](https://img.shields.io/badge/build-passing-gren)
![LICENSE](https://img.shields.io/badge/LICENSE-MIT-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![cryptography](https://img.shields.io/badge/cryptography-43.0.0-blue)
![pypdf](https://img.shields.io/badge/pypdf-5.4.0-blue)
![colorama](https://img.shields.io/badge/colorama-0.4.6-blue)
![pytest](https://img.shields.io/badge/pytest-8.3.5-blue)

# `pdfveil` - PDF暗号化CLIツール

PDFVeilは、AES-GCM暗号化を使用してPDFファイルを安全に暗号化および復号化するために設計されたコマンドラインツールです。 また、PDFメタデータを暗号化または非暗号化形式で保存するオプションも提供します。 このツールは、PDF文書を保護するためのシンプルで効率的な方法を提供することを目指しています。

## 特徴

- **PDF暗号化**: AES-GCMでPDFファイルを暗号化し、強力なセキュリティを確保します。
- **メタデータの暗号化**: デフォルトでPDFメタデータも暗号化する。
- **復号**: 正しいパスワードで暗号化されたPDFファイルを復号化します。
- **CLI操作**: コマンドラインから簡単に操作することができます。
- **強力な暗号化**: AES-256を用いてPDFを保護します。

## インストール

1. debパッケージをダウンロード  
   [pdfveil_0.1.0-1_all.deb](https://github.com/Saku0512/pdfveil/releases/download/v0.1/pdfveil_0.1.0-1_all.deb)  
   または、以下のコマンドでダウンロードしてください。  
   ```bash
   wget https://github.com/Saku0512/pdfveil/releases/download/v0.1/pdfveil_0.1.0-1_all.deb
   ```
2. インストール
   dpkgを使ってインストールしてください。
   ```bash
   sudo dpkg -i pdfveil_0.1.0-1_all.deb
   sudo apt install -f
   ```

## 使い方

`pdfveil`は、PDFファイルの暗号化と復号化をコマンドラインから操作できます。

### 暗号化
PDFファイルを暗号化するには、以下のコマンドを使用します
```bash
pdfveil encrypt input.pdf [--password password] [--output output] [--force] [--remove] [--no-encrypt-metadata]
```
- encrypt, enc : 暗号化を指定
- input.pdf : 対象PDF
- --password, -p : パスワードを指定(省略時はプロンプトで求められる)
- --output, -o : 出力ファイル名を指定(拡張子は指定不可)
- --force, -f : 既存ファイルを強制上書きする
- --remove : 暗号化後に元ファイル(input.pdf)を削除する
- --not-encrypt-metadata : メタデータを含めて暗号化しない

### 復号
VEILファイルを復号するには、以下のコマンドを使用します
```bash
pdfveil decrypt input.veil [--password password] [--output output] [--force] [--remove]
```
- decrypt, dec : 復号を指定
- --passwrod, -p : パスワードを指定(省略時はプロンプトで求められる)
- --output, -o : 出力ファイル名を指定(拡張子は指定不可)
- --force, -f : 既存ファイルを強制上書きする
- --remove : 復号後に元ファイル(input.veil)を削除する

## コントリビューション

`pdfveil`へのコントリビューションは歓迎します！以下の手順に従って、コントリビュートをお願いします。

### コミット規約

- 単一の目的のコミット : 一度のコミットで複数の変更を加えないようにしてください。例えば、バグ修正と機能追加は別々のコミットにしてください。
- わかりやすいコミットメッセージ : 変更の内容を簡潔に説明してください。
  - `fix: バグ修正`
  - `feature: 新機能の追加`
  - `tests: テストコードの追加・更新`
  - `ref: リファクタリング`
  - `docs: ドキュメントの更新`

### プルリクエストガイドライン

1. まずリポジトリをフォークしてローカルにクローンしてください。
2. 作業用に新しいブランチを作成してください。
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. 変更を行ったらコミット規則にのっとりコミットしてください。
4. テスト
   テストコードを作成・更新して正常に動作することを確かめてください。  
   テストは以下のコードで行えます。
   ```bash
   pytest tests/
   ```
6. プッシュ
   ```bash
   git push origin feature/my-new-feature
   ```
7. GitHubでプルリクエストを作成し、レビューを依頼してください。

## ライセンス

このプロジェクトは[MITライセンス](https://github.com/Saku0512/pdfveil/blob/main/LICENSE)の元で公開しています。
