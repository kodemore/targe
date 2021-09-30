from targe.policy import normalize_scope


def test_normalize_simple_scope() -> None:
    # when
    result = normalize_scope("test : test-2 : test-3")

    # then
    assert result == ["test:test-2:test-3"]


def test_normalize_scope_with_single_group() -> None:
    # when
    result = normalize_scope("test : test-1-1, test-1-2, test-1-3 : test-1-1-1")

    # then
    assert result == [
        "test:test-1-1:test-1-1-1",
        "test:test-1-2:test-1-1-1",
        "test:test-1-3:test-1-1-1"
    ]


def test_normalize_scope_with_multiple_groups() -> None:
    # when
    result = normalize_scope("test-a, test-b : test-1, test-2")

    # then
    assert result == [
        "test-a:test-1",
        "test-a:test-2",
        "test-b:test-1",
        "test-b:test-2",
    ]

    # when
    result = normalize_scope("test : test-a, test-b : test-1, test-2")

    # then
    assert result == [
        "test:test-a:test-1",
        "test:test-a:test-2",
        "test:test-b:test-1",
        "test:test-b:test-2",
    ]
