# ノート量産します

note向けの記事制作を少ない操作で進める、最小の編集室です。

## 現在できること
- GitHub Actions の「Run workflow」からテーマと記事数（1〜20）を指定してAI記事を生成
- `articles.json` に下書きを保存
- `index.html` を開き、一覧・本文確認・コピー・ローカルJSON読み込み
- **noteへの公開は自動実行しません。** 内容を確認してから投稿してください。

## 初期設定（1回だけ）
1. リポジトリの Settings → Secrets and variables → Actions → New repository secret に `OPENAI_API_KEY` を設定。**キーをコードや記事に書かない**。
2. Actions → 「Generate note drafts」→ Run workflow。テーマと記事数を指定。
3. 完了後の `articles.json` を `index.html` と同じフォルダで閲覧するか、画面の「JSONを読み込む」で選択する。
4. 必要なら Settings → Pages から main / root を公開元として指定すれば、一覧画面をスマートフォンから開けます。リポジトリはpublicなので**公開したくない下書きはGitHubへ保存しない**でください。

## 注意
- 最初は記事1本で起動確認。記事数を増やすのは確認後。
- ニュース、医療、法律、投資等の最新・高リスク情報を調べる仕組みは未実装。生成するのは一般的な読み物の草稿です。
- AIが実在しない統計・体験談・出典を作る可能性があります。必ず人間が確認してください。
- noteの公式個人向け一括投稿は未接続。ブラウザ操作や非公式APIも未実装です。
- OpenAI APIはChatGPT利用料金と別に従量課金されます。

## ファイル
- `generate.py`: OpenAI API を使った記事生成（標準ライブラリのみ）
- `.github/workflows/generate.yml`: GitHub Actionsから手動起動
- `index.html`: 軽量な下書き一覧・コピー
- `articles.json`: 生成された記事の保存先

**目的:** 自動制作により人間の操作を減らすこと。記事20本の生成と、利益・品質・noteへの自動投稿は別々に観測します。
