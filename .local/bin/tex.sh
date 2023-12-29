
# 引数が指定されていない場合はエラーメッセージを表示して終了
if [ -z "$1" ]; then
    echo "エラー: ファイル名が指定されていません。"
    echo "使用法: $0 ファイル名.py"
    exit 1
fi

# フォルダの作成（存在しない場合のみ）
mkdir -p "tex"

# DVIファイルの名前（拡張子なし）
dvi_file="${1%.tex}.dvi"

# PDFファイルの名前
pdf_file="${1%.tex}.pdf"

# platexでDVIを生成
platex -output-directory="tex" "$1"

cd tex
# dvipdfmxでPDFに変換
dvipdfmx -o "$pdf_file" "$dvi_file"


echo "PDFファイルが作成されました: $pdf_file"

