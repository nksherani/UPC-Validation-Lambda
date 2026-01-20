import base64
import json
import os
import tempfile
from typing import Any

from app.extractors.carelabel import extract_care_labels
from app.extractors.classifier import classify_pdf
from app.extractors.rfid import extract_hang_tags


def _normalize_items(items: list[dict[str, Any]], parent_info: dict[str, Any]) -> list[dict[str, Any]]:
    normalized = []
    for item in items:
        raw_item = dict(item)
        raw_item.pop("composition", None)
        merged = {
            "style_number": item.get("style_number") or parent_info.get("style_number"),
            "size": item.get("size"),
            "color": item.get("color") or parent_info.get("color"),
            "upc": item.get("upc") or item.get("barcode") or item.get("upc_candidate"),
            "raw": raw_item,
        }
        normalized.append(merged)
    return normalized


def _extract_from_paths(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    care_labels: list[dict[str, Any]] = []
    hang_tags: list[dict[str, Any]] = []

    for payload in payloads:
        tmp_path = payload["path"]
        classification = classify_pdf(tmp_path)
        if classification["type"] == "care_label":
            metadata = extract_care_labels(tmp_path)
            care_labels.extend(_normalize_items(metadata["care_labels"], metadata["parent_info"]))
        elif classification["type"] == "rfid":
            metadata = extract_hang_tags(tmp_path)
            hang_tags.extend(_normalize_items(metadata["hang_tags"], metadata["parent_info"]))
        else:
            metadata = extract_care_labels(tmp_path)
            if metadata["care_labels"]:
                care_labels.extend(_normalize_items(metadata["care_labels"], metadata["parent_info"]))
            else:
                metadata = extract_hang_tags(tmp_path)
                hang_tags.extend(_normalize_items(metadata["hang_tags"], metadata["parent_info"]))

    return {
        "care_labels": care_labels,
        "hang_tags": hang_tags,
    }


def _save_bytes_to_temp(content: bytes, filename: str | None) -> str:
    suffix = ".pdf" if filename and filename.lower().endswith(".pdf") else ""
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(content)
        return tmp.name


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    payload = event
    if isinstance(event.get("body"), str):
        body = event["body"]
        if event.get("isBase64Encoded"):
            try:
                body = base64.b64decode(body).decode("utf-8")
            except (ValueError, TypeError, UnicodeDecodeError):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Invalid base64 body."}),
                }
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return {
                "statusCode": 400,
                "body": json.dumps({"detail": "Invalid JSON body."}),
            }

    files = payload.get("files") if isinstance(payload, dict) else None
    if not isinstance(files, list) or not files:
        return {
            "statusCode": 400,
            "body": json.dumps({"detail": "No files provided."}),
        }

    payloads: list[dict[str, Any]] = []
    try:
        for entry in files:
            if not isinstance(entry, dict):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Invalid file entry."}),
                }

            content_type = entry.get("content_type")
            if content_type not in {"application/pdf", "application/x-pdf"}:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": f"Unsupported content_type: {content_type}"}),
                }

            b64_data = entry.get("base64")
            if not b64_data:
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Missing base64 data."}),
                }

            try:
                decoded = base64.b64decode(b64_data)
            except (ValueError, TypeError):
                return {
                    "statusCode": 400,
                    "body": json.dumps({"detail": "Invalid base64 data."}),
                }

            payloads.append({"path": _save_bytes_to_temp(decoded, entry.get("filename"))})

        result = _extract_from_paths(payloads)
        return {"statusCode": 200, "body": json.dumps(result)}
    finally:
        for payload in payloads:
            try:
                os.remove(payload["path"])
            except OSError:
                pass


