from collections import Counter
from flask import Flask, render_template, request
import re

app = Flask(__name__)

# ── Data ──────────────────────────────────────────────────────────────────────

GROCERY_CATEGORIES = {
    "PRODUCE": [
        "APPLE", "BANANA", "ORANGE", "LEMON", "LIME", "GRAPE", "STRAWBERRY",
        "BLUEBERRY", "RASPBERRY", "MANGO", "PINEAPPLE", "AVOCADO", "TOMATO",
        "LETTUCE", "SPINACH", "KALE", "BROCCOLI", "CAULIFLOWER", "CARROT",
        "CELERY", "CUCUMBER", "ZUCCHINI", "EGGPLANT", "ONION", "GARLIC",
        "POTATO", "SWEET POTATO", "PEPPER", "MUSHROOM", "CORN", "PARSLEY",
        "CILANTRO", "MINT", "SCALLION", "BEET", "CABBAGE",
    ],
    "DAIRY & EGGS": [
        "MILK", "BUTTER", "CHEESE", "YOGURT", "CREAM", "SOUR CREAM",
        "CREAM CHEESE", "COTTAGE CHEESE", "PARMESAN", "MOZZARELLA",
        "CHEDDAR", "FETA", "LEBEN", "LABANEH", "EGGS",
    ],
    "MEAT & SEAFOOD": [
        "CHICKEN", "BEEF", "TURKEY", "LAMB", "GROUND BEEF", "GROUND TURKEY",
        "SAUSAGE", "SALMON", "TUNA", "SHRIMP", "COD", "SCHNITZEL",
    ],
    "BAKERY": [
        "BREAD", "CHALLAH", "PITA", "BAGEL", "TORTILLA", "MUFFIN",
        "SOURDOUGH", "LAVASH", "ROLL", "BAGUETTE",
    ],
    "FROZEN": [
        "ICE CREAM", "FROZEN PIZZA", "FROZEN VEGETABLES", "FROZEN FRUIT",
        "WAFFLES", "EDAMAME", "FROZEN BURRITO",
    ],
    "PANTRY": [
        "PASTA", "RICE", "FLOUR", "SUGAR", "SALT", "OIL", "OLIVE OIL",
        "VINEGAR", "SOY SAUCE", "HONEY", "TAHINI", "HUMMUS", "JAM",
        "PEANUT BUTTER", "CEREAL", "OATS", "CRACKERS", "CHIPS", "BEANS",
        "LENTILS", "CHICKPEAS", "BROTH", "PASTA SAUCE", "KETCHUP", "MAYO",
        "MUSTARD", "SALSA", "MAPLE SYRUP", "BAMBA", "BISLI", "ZAATAR",
        "AMBA", "HARISSA",
    ],
    "BEVERAGES": [
        "WATER", "JUICE", "COFFEE", "TEA", "SODA", "WINE", "BEER",
        "SPARKLING WATER", "LEMONADE",
    ],
}

ITEM_PRICES = {
    # PRODUCE (₪)
    "APPLE": 7.00, "BANANA": 4.50, "ORANGE": 5.00, "LEMON": 2.00,
    "LIME": 3.00, "GRAPE": 12.00, "STRAWBERRY": 15.00, "BLUEBERRY": 20.00,
    "AVOCADO": 6.00, "TOMATO": 5.00, "LETTUCE": 6.00, "SPINACH": 8.00,
    "BROCCOLI": 10.00, "CARROT": 4.00, "ONION": 4.00, "GARLIC": 5.00,
    "POTATO": 5.00, "SWEET POTATO": 6.00, "PEPPER": 8.00, "MUSHROOM": 12.00,
    "CUCUMBER": 4.00, "ZUCCHINI": 6.00, "EGGPLANT": 7.00, "PARSLEY": 3.00,
    "CILANTRO": 3.00, "MINT": 3.00, "CORN": 5.00, "SCALLION": 4.00,
    "BEET": 5.00, "CABBAGE": 6.00,

    # DAIRY & EGGS
    "MILK": 6.00, "BUTTER": 14.00, "CHEESE": 20.00, "YOGURT": 8.00,
    "CREAM": 12.00, "SOUR CREAM": 9.00, "CREAM CHEESE": 15.00,
    "COTTAGE CHEESE": 8.00, "PARMESAN": 25.00, "MOZZARELLA": 18.00,
    "CHEDDAR": 20.00, "FETA": 18.00, "LEBEN": 5.00, "LABANEH": 12.00,
    "EGGS": 12.00,

    # MEAT & SEAFOOD
    "CHICKEN": 30.00, "BEEF": 60.00, "TURKEY": 35.00, "LAMB": 80.00,
    "GROUND BEEF": 45.00, "GROUND TURKEY": 32.00, "SAUSAGE": 28.00,
    "SALMON": 70.00, "TUNA": 10.00, "SHRIMP": 55.00, "COD": 50.00,
    "SCHNITZEL": 35.00,

    # BAKERY
    "BREAD": 8.00, "CHALLAH": 12.00, "PITA": 7.00, "BAGEL": 6.00,
    "TORTILLA": 10.00, "MUFFIN": 10.00, "SOURDOUGH": 18.00,
    "LAVASH": 8.00,

    # PANTRY
    "PASTA": 7.00, "RICE": 10.00, "FLOUR": 8.00, "SUGAR": 7.00,
    "SALT": 4.00, "OIL": 18.00, "OLIVE OIL": 30.00,
    "VINEGAR": 7.00, "SOY SAUCE": 10.00, "HONEY": 25.00,
    "TAHINI": 18.00, "HUMMUS": 12.00, "JAM": 15.00,
    "PEANUT BUTTER": 18.00, "CEREAL": 22.00, "OATS": 14.00,
    "CRACKERS": 12.00, "CHIPS": 12.00, "BEANS": 6.00,
    "LENTILS": 8.00, "CHICKPEAS": 7.00, "BROTH": 10.00,
    "PASTA SAUCE": 12.00, "KETCHUP": 10.00, "MAYO": 14.00,
    "MUSTARD": 10.00, "SALSA": 15.00, "MAPLE SYRUP": 35.00,
    "BAMBA": 7.00, "BISLI": 7.00, "ZAATAR": 12.00, "AMBA": 10.00,
    "HARISSA": 10.00,

    # BEVERAGES
    "WATER": 5.00, "JUICE": 15.00, "COFFEE": 40.00, "TEA": 20.00,
    "SODA": 8.00, "WINE": 50.00, "BEER": 20.00,
    "SPARKLING WATER": 7.00, "LEMONADE": 12.00,

    # FROZEN
    "ICE CREAM": 22.00, "FROZEN PIZZA": 30.00, "WAFFLES": 18.00,
    "FROZEN VEGETABLES": 12.00, "EDAMAME": 20.00,
}

# Israeli-relevant pairings: if you have X, you probably want Y
PAIRING_SUGGESTIONS = {
    "PITA":        ["HUMMUS", "TAHINI", "LABANEH", "ZAATAR", "FETA"],
    "HUMMUS":      ["PITA", "OLIVE OIL", "LEMON", "PARSLEY"],
    "TAHINI":      ["LEMON", "GARLIC", "PARSLEY"],
    "LABANEH":     ["OLIVE OIL", "ZAATAR", "TOMATO", "CUCUMBER"],
    "CHALLAH":     ["BUTTER", "HONEY", "EGGS", "JAM"],
    "EGGS":        ["BUTTER", "TOMATO", "ONION", "CHEESE"],
    "CHICKEN":     ["GARLIC", "LEMON", "OLIVE OIL", "ONION"],
    "SCHNITZEL":   ["LEMON", "POTATO", "MAYO", "KETCHUP"],
    "LAMB":        ["GARLIC", "MINT", "LEMON", "ONION"],
    "SALMON":      ["LEMON", "OLIVE OIL", "GARLIC", "DILL"],
    "GROUND BEEF": ["ONION", "GARLIC", "PASTA SAUCE", "PASTA"],
    "PASTA":       ["PASTA SAUCE", "PARMESAN", "GARLIC", "OLIVE OIL"],
    "RICE":        ["BROTH", "ONION", "OLIVE OIL", "CHICKEN"],
    "LENTILS":     ["ONION", "GARLIC", "LEMON", "CUMIN"],
    "CHICKPEAS":   ["TAHINI", "GARLIC", "LEMON", "OLIVE OIL"],
    "COFFEE":      ["MILK", "SUGAR", "CREAM"],
    "TEA":         ["HONEY", "LEMON", "MINT"],
    "WINE":        ["CHEESE", "CRACKERS", "GRAPE"],
    "BEER":        ["CHIPS", "BAMBA"],
    "OATS":        ["HONEY", "BANANA", "MILK"],
    "CEREAL":      ["MILK", "BANANA"],
    "ICE CREAM":   ["BANANA", "HONEY"],
    "EGGPLANT":    ["TAHINI", "GARLIC", "LEMON", "OLIVE OIL"],
    "TOMATO":      ["CUCUMBER", "ONION", "OLIVE OIL", "LEMON"],
    "ZAATAR":      ["OLIVE OIL", "PITA", "LABANEH"],
}

# ── Functions ─────────────────────────────────────────────────────────────────

def count_groceries(groceries: list[str]) -> list[tuple[str, int]]:
    """Count and deduplicate items, returning sorted (item, count) pairs."""
    items = [item.strip().upper() for item in groceries if item.strip()]
    return sorted([(item, count) for item, count in Counter(items).items()])

def parse_groceries(raw_lines: list[str]) -> list[str]:
    """
    Expand quantity notation into repeated items.
    Supports: 'tomatoes x3', 'tomatoes x 3', 'tomatoes 3x', '3x tomatoes', 'tomatoes (3)'
    'milk x2' → ['MILK', 'MILK']
    """
    expanded = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue

        qty = 1
        name = line

        patterns = [
            r'^(.+?)\s*[xX]\s*(\d+)$',   # tomatoes x3 / tomatoes X 3
            r'^(.+?)\s*\((\d+)\)$',        # tomatoes (3)
            r'^(\d+)\s*[xX]\s*(.+)$',      # 3x tomatoes
        ]

        for i, pattern in enumerate(patterns):
            match = re.match(pattern, line)
            if match:
                if i == 2:  # quantity-first pattern
                    qty = int(match.group(1))
                    name = match.group(2)
                else:
                    name = match.group(1)
                    qty = int(match.group(2))
                break

        expanded.extend([name.strip()] * qty)

    return expanded


def categorize_groceries(groceries: list[str]) -> dict[str, list[str]]:
    """Sort grocery items into store sections."""
    items = [item.strip().upper() for item in groceries if item.strip()]
    result: dict[str, list[str]] = {cat: [] for cat in GROCERY_CATEGORIES}
    result["OTHER"] = []

    for item in items:
        matched = False
        for category, keywords in GROCERY_CATEGORIES.items():
            if any(keyword in item or item in keyword for keyword in keywords):
                if item not in result[category]:
                    result[category].append(item)
                matched = True
                break
        if not matched and item not in result["OTHER"]:
            result["OTHER"].append(item)

    return {cat: sorted(vals) for cat, vals in result.items() if vals}


def estimate_budget_and_suggest(groceries: list[str]) -> dict:
    """
    Estimate total cost in Israeli shekels (₪) and suggest missing companions.

    Returns:
        priced_items:     dict of item -> price in ₪
        unknown_items:    items with no price match
        estimated_total:  sum of all priced items
        suggestions:      dict of item -> list of missing companions
    """
    items = [item.strip().upper() for item in groceries if item.strip()]
    item_set = set(items)

    priced: dict[str, float] = {}
    unknown: list[str] = []

    for item in items:
        if item in ITEM_PRICES:
            priced[item] = ITEM_PRICES[item]
        else:
            match = next(
                (key for key in ITEM_PRICES if key in item or item in key), None
            )
            if match:
                priced[item] = ITEM_PRICES[match]
            else:
                unknown.append(item)

    total = round(sum(priced.values()), 2)

    suggestions: dict[str, list[str]] = {}
    for item in items:
        for key, companions in PAIRING_SUGGESTIONS.items():
            if key in item or item in key:
                missing = [c for c in companions if c not in item_set]
                if missing:
                    suggestions[item] = missing
                break

    return {
        "priced_items": dict(sorted(priced.items())),
        "unknown_items": sorted(unknown),
        "estimated_total": total,
        "suggestions": suggestions,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
def index():
    counts = []
    categories = {}
    budget = {}

    if request.method == "POST":
        grocery_input = request.form.get("groceries", "")
        groceries = parse_groceries(grocery_input.splitlines())
        counts = count_groceries(groceries)
        categories = categorize_groceries(groceries)
        budget = estimate_budget_and_suggest(groceries)

    return render_template(
        "index.html",
        counts=counts,
        categories=categories,
        budget=budget,
    )


if __name__ == "__main__":
    app.run(debug=True)