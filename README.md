# toggl_analyzer
Togglの記録のローカルへの保存、可視化を行う

# Setting
動作環境
- windows 10 Pro (64bit)
- Python 3.6.1 | Anaconda 4.4.0 (64bit)

# Requirements
必要なライブラリ．同内容はrequirement.txtにも記載されている

最低限必要なもの
matplotlib==2.0.2
numpy==1.13.1
python-ternary==1.0.3

# Structure

```
C:.
│  main.py
│  README.md
│  run.bat
├─data ... tokenが記してある設定ファイルとローカルに落としてきたタスクのデータの保存場所
│   setting.json
├─graph_output ... 可視化した画像の保存場所
│   Barplot_2018-01-01_2018-02-28.png
│   Ternary_youbi.png
│   Timeline_2017-06-01_2017-07-31.png
└─source ... コード置き場
    analyzer.py ... データベースのファイルの解析ツール
    date_conv.py ... 日付データを扱うための便利ツール
    toggl_database_util.py ... データベースを最新版に更新したり、一部カットするなどのツール
    toggl_visualize_util.py ... グラフを可視化するためのツール
    toggl_wrapper.py ... データ取得のためのラッパー。取得漏れが無いように一日ずつ取って来たりしている

```

# Run
最上位のmain.pyを実行