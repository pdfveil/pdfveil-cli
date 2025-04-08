![Build](https://img.shields.io/badge/build-passing-green)
![LICENSE](https://img.shields.io/badge/LICENSE-MIT-green)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![cryptography](https://img.shields.io/badge/cryptography-43.0.0-blue)
![pypdf](https://img.shields.io/badge/pypdf-5.4.0-blue)
![colorama](https://img.shields.io/badge/colorama-0.4.6-blue)
![pytest](https://img.shields.io/badge/pytest-8.3.5-blue)

# `pdfveil` - PDF暗号化CLIツール

<p align="center">
  <img src="https://github.com/user-attachments/assets/9c094071-57b5-4224-ac0c-2ff4b7d9d219" alt="ロゴ" width="400px">
</p>

**pdfveil** は、PDFファイルを強力なAES-GCM方式で暗号化・復号するためのシンプルかつ安全なCLIツールです。  
メタデータの暗号化有無を選べる柔軟性と、扱いやすいコマンドライン操作を特徴としています。

---

## 🔒 主な機能

- **PDF暗号化（AES-GCM）**
- **メタデータの暗号化（デフォルトで有効）**
- **復号機能**
- **コマンドラインで簡単操作**
- **安全なパスワード管理（プロンプト入力対応）**

---

## 📦 インストール

1. **debパッケージをダウンロード**  
   [📎 pdfveil_0.1.0-1_all.deb](https://github.com/Saku0512/pdfveil/releases/download/v0.1/pdfveil_0.1.0-1_all.deb)

   または、以下で取得：
   ```bash
   wget https://github.com/Saku0512/pdfveil/releases/download/v0.1/pdfveil_0.1.0-1_all.deb
   ```

2. **インストール**
   ```bash
   sudo dpkg -i pdfveil_0.1.0-1_all.deb
   sudo apt install -f
   ```

---

## 🚀 使い方

### 🔐 暗号化

```bash
pdfveil encrypt input.pdf [--password password] [--output output] [--force] [--remove] [--no-encrypt-metadata]
```

#### オプション一覧

| オプション | 説明 |
|------------|------|
| `-p`, `--password` | パスワード（省略時はプロンプト） |
| `-o`, `--output` | 出力ファイル名（拡張子不要） |
| `-f`, `--force` | 既存ファイルの強制上書き |
| `--remove` | 元ファイル削除 |
| `--no-encrypt-metadata` | メタデータを暗号化しない |

---

### 🔓 復号

```bash
pdfveil decrypt input.veil [--password password] [--output output] [--force] [--remove]
```

| オプション | 説明 |
|------------|------|
| `-p`, `--password` | パスワード（省略時はプロンプト） |
| `-o`, `--output` | 出力ファイル名（拡張子不要） |
| `-f`, `--force` | 既存ファイルの強制上書き |
| `--remove` | 元ファイル削除 |

---

## 🤝 コントリビューション

**pdfveil** はオープンソースです。改善提案・バグ報告・機能追加、大歓迎です！

### ✅ コミットメッセージ規約

- 目的ごとにコミットを分ける
- プレフィックス例：
  - `fix:` バグ修正
  - `feature:` 新機能追加
  - `tests:` テスト追加・更新
  - `ref:` リファクタリング
  - `docs:` ドキュメント編集
  - `build` ビルド関係

### 🛠 プルリクエスト手順

1. フォークしてクローン
2. 新ブランチ作成：
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. 作業・コミット
4. テストコード作成  
   追加した機能が実際に動くか確かめるために`/tests`にテストコードを作成してください。
6. テスト実行：
   ```bash
   pytest tests/
   ```
7. プッシュ：
   ```bash
   git push origin feature/my-new-feature
   ```
8. GitHubでPRを作成

---

## 📄 ライセンス

このプロジェクトは [MITライセンス](https://github.com/Saku0512/pdfveil/blob/main/LICENSE) のもとで提供されています。

---

## 🛡 セキュリティに関するお知らせ

セキュリティポリシーはこちらをご覧ください：  
[🔐 SECURITY.md](https://github.com/Saku0512/pdfveil/blob/main/SECURITY.md)

