#!/usr/bin/env python3
"""Generate review-only note drafts. Python standard library, OpenAI API."""
import argparse
import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

PROMPT = """日本語のnote向けの記事草稿を1本書いてください。
テーマ: {topic}
記事番号: {number}/{total}
記事同士で切り口を変え、読者の具体的な疑問に応えてください。
事実未確認の数字、固有名詞、ニュース、出典、架空の実体験を捏造しない。
医療・金融・法律の助言、断定的な成果保証、煽り文句を避ける。
見出し付きの読みやすいMarkdown本文（目安600〜1000字）。
JSONオブジェクトのみで回答: {{"title":"題名","summary":"2文程度の概要","body":"Markdown本文","tags":["タグ1","タグ2"]}}"""

def generate(key: str, model: str, topic: str, number: int, total: int) -> dict:
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "あなたは慎重な日本語編集者です。JSON以外は返さないでください。"},
            {"role": "user", "content": PROMPT.format(topic=topic, number=number, total=total)}
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.75,
    }
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(data, ensure_ascii=False).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"API HTTP {error.code}: {details}") from error
    raw = payload["choices"][0]["message"]["content"]
    result = json.loads(raw)
    if not isinstance(result, dict) or any(not isinstance(result.get(k), str) or not result[k].strip()
                                         for k in ("title", "summary", "body")):
        raise ValueError("Unexpected article structure")
    tags = result.get("tags", [])
    if not isinstance(tags, list):
        tags = []
    return {
        "id": f"{dt.datetime.now(dt.timezone.utc):%Y%m%d}-{number:02d}",
        "title": result["title"].strip(),
        "summary": result["summary"].strip(),
        "body": result["body"].strip(),
        "tags": [str(t)[:30] for t in tags[:5]],
        "status": "draft",
    }

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", default="暮らしの小さな工夫")
    parser.add_argument("--count", type=int, default=1)
    parser.add_argument("--output", default="articles.json")
    parser.add_argument("--model", default=os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    args = parser.parse_args()
    if not 1 <= args.count <= 20:
        parser.error("--count must be 1..20")
    if len(args.topic) > 160 or not args.topic.strip():
        parser.error("--topic must be 1..160 characters")
    key = os.getenv("OPENAI_API_KEY", "").strip()
    if not key:
        sys.exit("OPENAI_API_KEY secret is required")
    articles = []
    for i in range(1, args.count + 1):
        article = generate(key, args.model, args.topic, i, args.count)
        articles.append(article)
        print(f"Generated {i}/{args.count}: {article['title']}", flush=True)
    output = {"generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
              "topic": args.topic, "articles": articles}
    Path(args.output).write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Saved {len(articles)} drafts in {args.output}")

if __name__ == "__main__":
    main()
