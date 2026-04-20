"""
Unit-тесты для функции transform() из etl_pipeline.py
Запуск: python -m pytest test_etl.py -v
"""

import pytest
from etl_pipeline import transform



FIXED_TS = "2024-01-15T12:00:00+00:00"

SAMPLE_POSTS = [
    {"userId": 1, "id": 1, "title": "hello world",  "body": "body one"},
    {"userId": 1, "id": 2, "title": "second post",  "body": "body two"},
    {"userId": 2, "id": 3, "title": "third entry",  "body": "body three"},
    {"userId": 2, "id": 4, "title": "fourth item",  "body": "body four"},
    {"userId": 3, "id": 5, "title": "fifth record", "body": "body five"},
]



def test_output_fields():
    result = transform(SAMPLE_POSTS[:1], timestamp=FIXED_TS)
    assert len(result) == 1
    keys = set(result[0].keys())
    assert keys == {"userId", "id", "title", "body", "timestamp"}


def test_title_uppercase():
    result = transform(SAMPLE_POSTS, timestamp=FIXED_TS)
    for record in result:
        assert record["title"] == record["title"].upper(), (
            f"title не в верхнем регистре: {record['title']!r}"
        )


def test_timestamp_injected():
    result = transform(SAMPLE_POSTS, timestamp=FIXED_TS)
    for record in result:
        assert record["timestamp"] == FIXED_TS


def test_incremental_filter_basic():
    result = transform(SAMPLE_POSTS, last_id=3, timestamp=FIXED_TS)
    ids = [r["id"] for r in result]
    assert ids == [4, 5], f"Ожидали [4, 5], получили {ids}"


def test_incremental_filter_all_new():
    """last_id=0 → все записи проходят фильтр"""
    result = transform(SAMPLE_POSTS, last_id=0, timestamp=FIXED_TS)
    assert len(result) == len(SAMPLE_POSTS)


def test_incremental_filter_all_old():
    """last_id >= max id → ни одна запись не проходит"""
    result = transform(SAMPLE_POSTS, last_id=100, timestamp=FIXED_TS)
    assert result == []


def test_incremental_filter_exact_boundary():
    """id == last_id тоже фильтруется (строгое >)"""
    result = transform(SAMPLE_POSTS, last_id=5, timestamp=FIXED_TS)
    assert result == []


def test_empty_input():
    result = transform([], timestamp=FIXED_TS)
    assert result == []


def test_input_not_mutated():
    original_titles = [p["title"] for p in SAMPLE_POSTS]
    transform(SAMPLE_POSTS, timestamp=FIXED_TS)
    for post, orig_title in zip(SAMPLE_POSTS, original_titles):
        assert post["title"] == orig_title, "transform() изменила исходные данные"


def test_title_with_special_chars():
    posts = [{"userId": 1, "id": 1, "title": "hello, world! 123", "body": "x"}]
    result = transform(posts, timestamp=FIXED_TS)
    assert result[0]["title"] == "HELLO, WORLD! 123"


def test_body_unchanged():
    posts = [{"userId": 1, "id": 1, "title": "t", "body": "original body\nnewline"}]
    result = transform(posts, timestamp=FIXED_TS)
    assert result[0]["body"] == "original body\nnewline"


def test_order_preserved():
    result = transform(SAMPLE_POSTS, last_id=0, timestamp=FIXED_TS)
    ids = [r["id"] for r in result]
    assert ids == sorted(ids)


def test_ids_preserved():
    result = transform(SAMPLE_POSTS, last_id=0, timestamp=FIXED_TS)
    for original, transformed in zip(SAMPLE_POSTS, result):
        assert transformed["userId"] == original["userId"]
        assert transformed["id"]     == original["id"]