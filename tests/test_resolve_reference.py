from toffi.utils import resolve_reference


def test_resolve_reference() -> None:
    # given
    reference = "some:reference"

    # when
    resolved = resolve_reference({}, reference)

    # then
    assert resolved == "some:reference"


def test_resolve_reference_with_simple_var() -> None:
    # given
    reference = "some:{ var }"

    # when
    resolved = resolve_reference({"var": 12}, reference)

    # then
    assert resolved == "some:12"


def test_resolve_reference_with_deep_var() -> None:
    # given
    class ValueClass:
        def __init__(self, value):
            self.value = value

    reference = "var:{ var.sub_var.value }"
    var = {
        "var": {
            "sub_var": ValueClass("test")
        }
    }

    # when
    resolved = resolve_reference(var, reference)

    # then
    assert resolved == "var:test"
