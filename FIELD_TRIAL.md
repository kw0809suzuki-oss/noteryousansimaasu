# GitHub Field Agent｜既存note生成機からの転用試験 v0.1

既存の `generate.py`、`.github/workflows/generate.yml`、`articles.json`、`index.html` を変更せず、同じ **Python標準ライブラリ + GitHub Actions + OPENAI_API_KEY** の構成で、小さな研究・変更循環を試す。noteへの自動投稿は追加しない。

## 親目的

外部の現実を調べ、現在の実装へ照合し、必要なら小さな変更候補を試し、確認した結果が**次回の実動作**へ作用すること。記録や新しい機能を増やすこと自体は目的でない。

## 今回の実物

- `field_agent.py`: 有効なルールをファイルから読み、候補と旧版を同一入力で比較。採用後の実行動作とAPI使用量を `field_runs.json` に保存（直近20件）。
- `field_rules.py`: バージョン付きの可変部品。「一次資料を何件読んでから検証へ進むか」（0または1）が実際の次動作に作用する。
- `tests/test_field_agent.py`: API不要の5テスト。2回続けて実行し、1回目に採用したルールが2回目の選択を変えることを確認する。
- `.github/workflows/field-agent.yml`: PRでは**API費用0のテストのみ**。手動起動だけ `demo`（APIなし）か `live`（APIを最大1回）を選べる。定期実行なし。

## ローカルで実際に試した結果（2026-10-23）

```sh
python3 -m unittest discover -s tests -v
python3 field_agent.py --mode demo
python3 field_agent.py --mode demo
```

5テストPASS。1回目は v1 から v2 を採用し、未確認資料への次手が `run_research_probe` → `read_primary_source` に変化。2回目は**ファイルに保存したv2を再読し、開始時点から `read_primary_source` を選択**した。同じ変更は再採用しない。2回ともモデル呼び出しは0回。

これは「限定部品への変更が次の動作へ届いた」証拠であり、自律的なコード生成・研究能力の向上や長期学習の証明ではない。入力は合成例。任意Pythonコードの実行・改変は今回の範囲外。

## APIと費用

既存のnote投稿機では2026-10-11にOpenAI APIを使ったGitHub Actions成功記録がある。ただし **現在のキーの有効性は未確認**。この試験のPRはキーを使わず、モデル呼び出しもない。

`live` は指定された `https://arxiv.org/abs/...` の公開要旨を直接読み、OpenAI Chat Completionsを最大1回呼んで提案を得る。ウェブ全体の検索や無限ループはしない。APIは別料金。利用したモデルのトークン数は実行記録に残す。公開リポジトリなので秘密や非公開資料を記録しない。

手動運転の結果はGitHub Actions artifactに出す。`experiment/` ブランチの場合に限り試験結果をコミットする。mainへの自動コミット・note自動投稿・定期実行はない。

新設した手動workflowは、GitHubの制約によりdefault branchへ存在するまでUIで起動できない場合がある。最初はPRから発動する無課金のCIで試験する。

## 次へつなぐには

自由なソースコード改修へ拡張する場合は、候補パッチを別ブランチへ保存し、**モデルの生成コードを秘密鍵のあるジョブでは実行せず**、無認証のCIでテストしてから採用する経路を別途作る。現在の一変数ルールだけで自律的な機能開発を実現したとは見なさない。

判断を引き継ぐときは「重要だったこと」「理由」「判断を変える条件」を合わせて記録する。今回の重要点は、説明ではなく**次回の動作が変わること**。もし次回の実動作に作用しないなら転用方式を再検討する。
