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

## 実API運転の追加実測（2026-10-23 JST）

- Actions: https://github.com/kw0809suzuki-oss/noteryousansimaasu/actions/runs/39872144045 成功
- 対象一次資料: https://arxiv.org/abs/2505.06120 （現物取得＋SHA256を `field_runs.json` に記録）
- `gpt-4o-mini` Chat Completionsを1回だけ実行。入力1223、出力102、計**1325トークン**。
- 旧部品 v1 (`MIN_VERIFIED_SOURCES=0`) → 候補 v2 (`=1`) の固定2ケース比較はPASS。`unverified` の次動作を `run_research_probe` から `read_primary_source` へ変更し、結果を実際の `field_rules.py` / `field_runs.json` へコミット。
- 今回は最初に一次資料を取得しているので、**当該実行中**の `decision_before` / `decision_after` は両方 `run_research_probe` のまま。変更は資料未読の次回条件で作用する。採用判断が妥当である証明ではない。
- **発見した欠陥**：モデルが文章で提案したのは「マルチターン会話中に依頼を再確認する仕組み」。しかし数値候補は `MIN_VERIFIED_SOURCES=1` で、具体的な改善内容と変更先が一致しない。機械的fixture合格だけで自動採用したことが実際に観測された。現部品v2は実験ブランチ内に残すが、改善成功とみなさない。
- **次の判断を変える条件**：提案した問題・修正対象・評価結果が意味的にもつながっていることを別の観測で確認できた場合は維持・拡張を検討。逆に説明と変更先の不一致が解決できなければ採用条件を再考し、v1への復元も選択肢とする。
- 1回限りの有料実行用workflowと起動ファイルは実行後に削除。定期実行は設定していない。mainも未変更。

