import subprocess
import pytest

def test_man_pdfveil():
    # `man pdfveil` を実行
    result = subprocess.run(
        ["man", "pdfveil"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # manページが存在すれば終了コードは0
    assert result.returncode == 0, "manコマンドでpdfveilが表示できません"

    # 出力内容が空でない（念のため）
    assert result.stdout, "man出力が空です"

    # stderrにエラーが出ていない
    assert b'No manual entry' not in result.stderr, "manページが見つかりません"
