import pytest

from service_body_test import Order


@pytest.mark.parametrize(
    ("items", "expected"),
    [
        ([], 0),
        ([{"price": 10, "quantity": 1}], 10),
        ([{"price": 10, "quantity": 2}, {"price": 3.5, "quantity": 4}], 34),
        ([{"price": 0, "quantity": 7}, {"price": 12, "quantity": 0}], 0),
        ([{"price": 1.25, "quantity": 4}, {"price": 2.5, "quantity": 2}], 10.0),
    ],
)
def test_total_for_various_item_sets(items, expected):
    assert Order(1, items).total() == pytest.approx(expected)


def test_most_expensive_returns_item_with_highest_price():
    cheapest = {"price": 5, "quantity": 10}
    most_expensive = {"price": 99, "quantity": 1}
    middle = {"price": 20, "quantity": 3}
    assert Order(2, [cheapest, most_expensive, middle]).most_expensive() is most_expensive


def test_most_expensive_with_tied_prices_returns_first_matching_item():
    first = {"price": 10, "quantity": 1}
    second = {"price": 10, "quantity": 2}
    assert Order(3, [first, second]).most_expensive() is first


def test_most_expensive_on_empty_items_raises_value_error():
    with pytest.raises(ValueError):
        Order(4, []).most_expensive()


@pytest.mark.parametrize("percent", [0, 10, 25, 50, 100, 12.5])
def test_apply_discount_accepts_valid_percentages(percent):
    items = [{"price": 80.0, "quantity": 2}, {"price": 20.0, "quantity": 3}]
    order = Order(5, items)
    original_prices = [item["price"] for item in items]

    order.apply_discount(percent)

    for item, original_price in zip(items, original_prices):
        assert item["price"] == pytest.approx(original_price * (1 - percent / 100))


@pytest.mark.parametrize("percent", [-0.01, -1, 100.01, 101, float("inf"), float("-inf"), float("nan")])
def test_apply_discount_rejects_invalid_percentages(percent):
    order = Order(6, [{"price": 50.0, "quantity": 1}])
    with pytest.raises(ValueError, match="Invalid discount"):
        order.apply_discount(percent)


@pytest.mark.parametrize(
    ("percent", "expected_prices"),
    [
        (0, [10.0, 25.0, 100.0]),
        (50, [5.0, 12.5, 50.0]),
        (100, [0.0, 0.0, 0.0]),
    ],
)
def test_discount_updates_every_item_price(percent, expected_prices):
    items = [{"price": 10.0, "quantity": 1}, {"price": 25.0, "quantity": 2}, {"price": 100.0, "quantity": 1}]
    Order(7, items).apply_discount(percent)
    assert [item["price"] for item in items] == pytest.approx(expected_prices)


def test_invalid_discount_does_not_change_any_prices():
    items = [{"price": 10.0, "quantity": 1}, {"price": 25.0, "quantity": 2}]
    order = Order(8, items)
    with pytest.raises(ValueError):
        order.apply_discount(101)
    assert [item["price"] for item in items] == [10.0, 25.0]


def test_apply_discount_on_empty_items_is_valid_and_does_nothing():
    order = Order(9, [])
    order.apply_discount(20)
    assert order.items == []
    assert order.total() == 0


def test_repr_includes_order_id_and_item_count():
    order = Order("A-123", [{"price": 10, "quantity": 1}, {"price": 20, "quantity": 2}])
    assert repr(order) == "<Order A-123: 2 items>"


def test_repr_for_empty_order():
    assert repr(Order(0, [])) == "<Order 0: 0 items>"
