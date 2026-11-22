import pytest
from day05 import (
    count_groceries,
    categorize_groceries,
    estimate_budget_and_suggest,
    parse_groceries,
)


# ── parse_groceries ───────────────────────────────────────────────────────────

class TestParseGroceries:

    def test_plain_item_passes_through(self):
        assert parse_groceries(["milk"]) == ["milk"]

    def test_quantity_suffix(self):
        assert parse_groceries(["tomatoes x3"]) == ["tomatoes", "tomatoes", "tomatoes"]

    def test_quantity_suffix_with_space(self):
        assert parse_groceries(["eggs x 6"]) == ["eggs"] * 6

    def test_quantity_prefix(self):
        assert parse_groceries(["3x tomatoes"]) == ["tomatoes", "tomatoes", "tomatoes"]

    def test_quantity_in_parentheses(self):
        assert parse_groceries(["milk (2)"]) == ["milk", "milk"]

    def test_uppercase_x(self):
        assert parse_groceries(["bread X2"]) == ["bread", "bread"]

    def test_blank_lines_ignored(self):
        assert parse_groceries(["", "  ", "milk"]) == ["milk"]

    def test_multiple_items_mixed(self):
        result = parse_groceries(["milk x2", "bread", "eggs x3"])
        assert result == ["milk", "milk", "bread", "eggs", "eggs", "eggs"]

    def test_quantity_one_unchanged(self):
        assert parse_groceries(["milk x1"]) == ["milk"]


# ── count_groceries ───────────────────────────────────────────────────────────

class TestCountGroceries:

    def test_single_item(self):
        assert count_groceries(["milk"]) == [("MILK", 1)]

    def test_duplicates_counted(self):
        result = dict(count_groceries(["milk", "milk", "milk"]))
        assert result["MILK"] == 3

    def test_case_insensitive(self):
        result = dict(count_groceries(["Milk", "MILK", "milk"]))
        assert result["MILK"] == 3

    def test_whitespace_stripped(self):
        result = dict(count_groceries(["  milk  ", "milk"]))
        assert result["MILK"] == 2

    def test_empty_lines_ignored(self):
        assert count_groceries(["", "  ", ""]) == []

    def test_multiple_distinct_items(self):
        result = dict(count_groceries(["milk", "bread", "eggs"]))
        assert result == {"MILK": 1, "BREAD": 1, "EGGS": 1}

    def test_result_is_sorted(self):
        items, _ = zip(*count_groceries(["zucchini", "apple", "milk"]))
        assert list(items) == sorted(items)

    def test_mixed_duplicates_and_singles(self):
        result = dict(count_groceries(["milk", "eggs", "milk", "bread", "eggs", "milk"]))
        assert result["MILK"] == 3
        assert result["EGGS"] == 2
        assert result["BREAD"] == 1


# ── categorize_groceries ──────────────────────────────────────────────────────

class TestCategorizeGroceries:

    def test_known_produce_item(self):
        result = categorize_groceries(["tomato"])
        assert "PRODUCE" in result
        assert "TOMATO" in result["PRODUCE"]

    def test_known_dairy_item(self):
        result = categorize_groceries(["milk"])
        assert "DAIRY & EGGS" in result
        assert "MILK" in result["DAIRY & EGGS"]

    def test_known_meat_item(self):
        result = categorize_groceries(["chicken"])
        assert "MEAT & SEAFOOD" in result

    def test_known_pantry_item(self):
        result = categorize_groceries(["tahini"])
        assert "PANTRY" in result

    def test_unknown_item_goes_to_other(self):
        result = categorize_groceries(["dragonfruitXYZ"])
        assert "OTHER" in result

    def test_empty_categories_not_returned(self):
        result = categorize_groceries(["milk"])
        assert "FROZEN" not in result
        assert "BEVERAGES" not in result

    def test_items_sorted_within_category(self):
        result = categorize_groceries(["tomato", "apple", "banana"])
        produce = result.get("PRODUCE", [])
        assert produce == sorted(produce)

    def test_no_duplicates_in_category(self):
        result = categorize_groceries(["milk", "milk", "milk"])
        assert result.get("DAIRY & EGGS", []).count("MILK") == 1

    def test_partial_match(self):
        # "GREEK YOGURT" should still land in DAIRY via partial match on YOGURT
        result = categorize_groceries(["greek yogurt"])
        assert "DAIRY & EGGS" in result

    def test_multiple_categories_at_once(self):
        result = categorize_groceries(["milk", "chicken", "apple", "pasta"])
        assert "DAIRY & EGGS" in result
        assert "MEAT & SEAFOOD" in result
        assert "PRODUCE" in result
        assert "PANTRY" in result


# ── estimate_budget_and_suggest ───────────────────────────────────────────────

class TestEstimateBudgetAndSuggest:

    def test_known_item_has_price(self):
        result = estimate_budget_and_suggest(["milk"])
        assert "MILK" in result["priced_items"]
        assert result["priced_items"]["MILK"] > 0

    def test_unknown_item_flagged(self):
        result = estimate_budget_and_suggest(["unobtainium"])
        assert "UNOBTAINIUM" in result["unknown_items"]

    def test_total_is_sum_of_prices(self):
        result = estimate_budget_and_suggest(["milk", "eggs"])
        expected = result["priced_items"].get("MILK", 0) + result["priced_items"].get("EGGS", 0)
        assert result["estimated_total"] == round(expected, 2)

    def test_total_is_zero_for_all_unknowns(self):
        result = estimate_budget_and_suggest(["unobtainium", "flibbertigibbet"])
        assert result["estimated_total"] == 0.0

    def test_pita_suggests_hummus(self):
        result = estimate_budget_and_suggest(["pita"])
        assert "PITA" in result["suggestions"]
        assert "HUMMUS" in result["suggestions"]["PITA"]

    def test_no_suggestion_for_item_already_on_list(self):
        # If hummus is already on the list, it shouldn't be suggested alongside pita
        result = estimate_budget_and_suggest(["pita", "hummus"])
        suggestions = result["suggestions"].get("PITA", [])
        assert "HUMMUS" not in suggestions

    def test_no_suggestions_when_all_companions_present(self):
        # Add all pita companions — no suggestion card should appear for pita
        result = estimate_budget_and_suggest(
            ["pita", "hummus", "tahini", "labaneh", "zaatar", "feta"]
        )
        assert "PITA" not in result["suggestions"]

    def test_partial_price_match(self):
        # "ORGANIC TOMATO" should match TOMATO in the price DB
        result = estimate_budget_and_suggest(["organic tomato"])
        assert "ORGANIC TOMATO" in result["priced_items"]

    def test_prices_are_in_shekels_range(self):
        # Sanity check: a typical basket shouldn't cost less than ₪5 or more than ₪500
        items = ["milk", "eggs", "bread", "chicken", "tomato", "olive oil"]
        result = estimate_budget_and_suggest(items)
        assert 5 < result["estimated_total"] < 500

    def test_empty_list_returns_zero_total(self):
        result = estimate_budget_and_suggest([])
        assert result["estimated_total"] == 0.0
        assert result["priced_items"] == {}
        assert result["suggestions"] == {}