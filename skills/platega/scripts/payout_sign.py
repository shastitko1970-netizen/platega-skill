#!/usr/bin/env python3
"""HMAC-SHA256 signer for Platega Payout API.

Matches the official Python sample from docs.platega.io
("Create a RUB card payout via Payout API", re-read 2026-09-02, unchanged).

Prints Authorization and, for POST, Idempotency-Key. Does not send the request
unless --execute is passed. No secrets are hardcoded.

string_to_sign:

  POST payouts:  METHOD\\nPATH\\ntimestamp\\nidempotency-key\\nsha256_hex(body)
  GET cards:     METHOD\\nPATH\\ntimestamp\\n\\nsha256_hex(empty)

empty body SHA-256:
  e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855

Body MUST be serialized with separators=(",", ":") and those exact bytes
must be sent (requests data=, not json=).

Usage:
  export PLATEGA_MERCHANT_ID='your-merchant-uuid'
  export PLATEGA_PAYOUT_SECRET='your-payout-secret'

  python payout_sign.py --body '{"cardNumber":"2200000000000000","amountRub":1500,"payoutMethod":"CARD","currencyRequested":"RUB"}'

  python payout_sign.py --method GET --path /api/v1/cards
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import os
import sys
import time
import uuid


EMPTY_BODY_SHA256 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
DEFAULT_BASE = "https://app.platega.io"
DEFAULT_POST_PATH = "/api/v1/payouts/card-rub"
DEFAULT_GET_PATH = "/api/v1/cards"


def compact_json_bytes(raw: str) -> bytes:
    """Parse JSON then dump with official separators so the hash is stable."""
    obj = json.loads(raw)
    return json.dumps(obj, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sign(
    *,
    secret: str,
    method: str,
    path: str,
    timestamp: int,
    idempotency_key: str,
    body_bytes: bytes,
) -> tuple[str, str]:
    body_hash = hashlib.sha256(body_bytes).hexdigest()
    string_to_sign = "\n".join(
        [method.upper(), path, str(timestamp), idempotency_key, body_hash]
    )
    sig = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            string_to_sign.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("ascii")
    return sig, body_hash


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sign a Platega Payout API request (PG-HMAC-SHA256)."
    )
    parser.add_argument(
        "--merchant-id",
        default=os.environ.get("PLATEGA_MERCHANT_ID", ""),
        help="Merchant UUID (or env PLATEGA_MERCHANT_ID)",
    )
    parser.add_argument(
        "--secret",
        default=os.environ.get("PLATEGA_PAYOUT_SECRET", ""),
        help="Payout SECRET (or env PLATEGA_PAYOUT_SECRET). Never commit this.",
    )
    parser.add_argument("--method", default="POST", help="HTTP method (POST or GET)")
    parser.add_argument(
        "--path",
        default="",
        help="URL path. Default: /api/v1/payouts/card-rub (POST) or /api/v1/cards (GET)",
    )
    parser.add_argument(
        "--body",
        default="",
        help="JSON object for POST. Serialized with separators=(\",\", \":\")",
    )
    parser.add_argument(
        "--body-file",
        default="",
        help="Read JSON body from a file instead of --body",
    )
    parser.add_argument(
        "--idempotency-key",
        default="",
        help="Reuse a key for an idempotent POST retry. Default: new UUID",
    )
    parser.add_argument(
        "--timestamp",
        type=int,
        default=0,
        help="Unix seconds. Default: now. Server window is ±300s",
    )
    parser.add_argument(
        "--base",
        default=os.environ.get("PLATEGA_BASE_URL", DEFAULT_BASE),
        help="Base URL (default https://app.platega.io)",
    )
    parser.add_argument(
        "--print-string-to-sign",
        action="store_true",
        help="Also print the five-line string_to_sign and body hash",
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="POST/GET the signed request via urllib (optional)",
    )
    args = parser.parse_args(argv)

    method = args.method.upper()
    if method not in {"POST", "GET"}:
        print("error: --method must be POST or GET", file=sys.stderr)
        return 2

    path = args.path or (DEFAULT_GET_PATH if method == "GET" else DEFAULT_POST_PATH)
    if not path.startswith("/"):
        print("error: --path must start with /", file=sys.stderr)
        return 2

    if not args.merchant_id or not args.secret:
        print(
            "error: set --merchant-id / --secret or "
            "PLATEGA_MERCHANT_ID / PLATEGA_PAYOUT_SECRET",
            file=sys.stderr,
        )
        return 2

    if method == "GET":
        if args.body or args.body_file:
            print("error: GET must not have a body (hash of empty bytes)", file=sys.stderr)
            return 2
        body_bytes = b""
        idem_key = ""
    else:
        raw = args.body
        if args.body_file:
            with open(args.body_file, encoding="utf-8") as fh:
                raw = fh.read()
        if not raw:
            print("error: POST requires --body or --body-file", file=sys.stderr)
            return 2
        try:
            body_bytes = compact_json_bytes(raw)
        except json.JSONDecodeError as exc:
            print(f"error: invalid JSON body: {exc}", file=sys.stderr)
            return 2
        idem_key = args.idempotency_key or str(uuid.uuid4())

    ts = args.timestamp or int(time.time())
    sig, body_hash = sign(
        secret=args.secret,
        method=method,
        path=path,
        timestamp=ts,
        idempotency_key=idem_key,
        body_bytes=body_bytes,
    )
    authorization = f"PG-HMAC kid={args.merchant_id}, ts={ts}, sig={sig}"

    print(f"Authorization: {authorization}")
    if method == "POST":
        print(f"Idempotency-Key: {idem_key}")
    print("Content-Type: application/json")
    if args.print_string_to_sign:
        string_to_sign = "\n".join(
            [method, path, str(ts), idem_key, body_hash]
        )
        print("---")
        print("string_to_sign:")
        print(string_to_sign)
        print(f"body_sha256_hex: {body_hash}")
        if method == "GET" and body_hash != EMPTY_BODY_SHA256:
            print("warning: empty-body hash mismatch", file=sys.stderr)
        if method == "POST":
            print(f"body_bytes: {body_bytes.decode('utf-8')}")

    if args.execute:
        import urllib.error
        import urllib.request

        headers = {
            "Authorization": authorization,
            "Content-Type": "application/json",
        }
        if method == "POST":
            headers["Idempotency-Key"] = idem_key
        req = urllib.request.Request(
            args.base.rstrip("/") + path,
            data=body_bytes if method == "POST" else None,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print("---")
                print(f"HTTP {resp.status}")
                print(resp.read().decode("utf-8", errors="replace"))
        except urllib.error.HTTPError as exc:
            print("---")
            print(f"HTTP {exc.code}")
            print(exc.read().decode("utf-8", errors="replace"))
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
