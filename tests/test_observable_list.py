from toffi.utils import ObservableList


def test_can_instantiate() -> None:
    # given
    instance = ObservableList([1, 2, 3], lambda x: x)

    # then
    assert isinstance(instance, ObservableList)


def test_on_change_listener() -> None:
    # given
    states = []
    instance = ObservableList([1, 2], lambda x: states.append(x))

    # when
    instance.append(3)
    instance.append(4)

    # then
    assert len(states) == 2
