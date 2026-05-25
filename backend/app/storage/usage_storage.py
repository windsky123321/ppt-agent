from __future__ import annotations

import csv
import json
import logging
import os
import time
from collections import defaultdict
from pathlib import Path

from app.runtime_paths import usage_root
from app.schemas.usage import UsageRecord, UsageSummary, UsageTaskDetail


logger = logging.getLogger(__name__)


class UsageStorage:
    def __init__(self) -> None:
        self.root = Path()
        self.jsonl_path = Path()
        self._sync_paths()
        self.root.mkdir(parents=True, exist_ok=True)

    def record(self, record: UsageRecord) -> UsageRecord:
        self._sync_paths()
        self.root.mkdir(parents=True, exist_ok=True)
        payload = json.dumps(record.model_dump(), ensure_ascii=False) + "\n"
        for attempt in range(5):
            try:
                with self.jsonl_path.open("a", encoding="utf-8") as handle:
                    handle.write(payload)
                break
            except PermissionError:
                fallback_path = self.root / f"usage-{os.getpid()}.jsonl"
                try:
                    with fallback_path.open("a", encoding="utf-8") as handle:
                        handle.write(payload)
                    break
                except PermissionError:
                    if attempt == 4:
                        raise
                time.sleep(0.05 * (attempt + 1))
        logger.info(
            "usage recorded: task=%s stage=%s model=%s mock=%s",
            record.task_id,
            record.stage,
            record.model,
            record.mock,
        )
        return record

    def list_records(self) -> list[UsageRecord]:
        self._sync_paths()
        jsonl_files = sorted(self.root.glob("usage*.jsonl"))
        if not jsonl_files:
            return []
        records: list[UsageRecord] = []
        for file_path in jsonl_files:
            for line in file_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                records.append(UsageRecord(**json.loads(line)))
        return records

    def summary(self) -> UsageSummary:
        records = self.list_records()
        summary = UsageSummary(total_records=len(records))
        prompt_tokens = 0
        completion_tokens = 0
        total_tokens = 0
        estimated_cost = 0.0
        has_prompt = False
        has_completion = False
        has_total = False
        has_cost = False
        for record in records:
            summary.total_request_count += record.request_count
            summary.total_retry_count += record.retry_count
            summary.total_error_count += record.error_count
            if not record.provider_usage_available:
                summary.unknown_usage_records += 1
            if record.prompt_tokens is not None:
                prompt_tokens += record.prompt_tokens
                has_prompt = True
            if record.completion_tokens is not None:
                completion_tokens += record.completion_tokens
                has_completion = True
            if record.total_tokens is not None:
                total_tokens += record.total_tokens
                has_total = True
            if record.estimated_cost is not None:
                estimated_cost += record.estimated_cost
                has_cost = True
        summary.total_prompt_tokens = prompt_tokens if has_prompt else None
        summary.total_completion_tokens = completion_tokens if has_completion else None
        summary.total_tokens = total_tokens if has_total else None
        summary.total_estimated_cost = round(estimated_cost, 6) if has_cost else None
        return summary

    def tasks(self) -> list[UsageTaskDetail]:
        grouped: dict[str, list[UsageRecord]] = defaultdict(list)
        for record in self.list_records():
            grouped[record.task_id].append(record)
        return [UsageTaskDetail(task_id=task_id, records=records) for task_id, records in sorted(grouped.items(), reverse=True)]

    def task_detail(self, task_id: str) -> UsageTaskDetail:
        records = [item for item in self.list_records() if item.task_id == task_id]
        if not records:
            raise FileNotFoundError(task_id)
        return UsageTaskDetail(task_id=task_id, records=records)

    def export_csv(self, target_path: Path) -> Path:
        records = self.list_records()
        with target_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(UsageRecord.model_fields.keys()))
            writer.writeheader()
            for record in records:
                writer.writerow(record.model_dump())
        logger.info("usage exported csv: %s", target_path)
        return target_path

    def export_json(self, target_path: Path) -> Path:
        target_path.write_text(
            json.dumps([item.model_dump() for item in self.list_records()], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        logger.info("usage exported json: %s", target_path)
        return target_path

    def clear(self) -> None:
        for file_path in self.root.glob("usage*.jsonl"):
            file_path.unlink()
        logger.info("usage cleared")

    def _sync_paths(self) -> None:
        self.root = usage_root()
        self.jsonl_path = self.root / "usage.jsonl"
