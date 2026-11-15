from collections import Counter
from flask import Flask, render_template, request

app = Flask(__name__)


def count_groceries(groceries: list[str]) -> list[tuple[str, int]]:
    groceries = [item.strip().upper() for item in groceries if item.strip()]
    return sorted(
        [(item, count) for item, count in Counter(groceries).items()]
    )


@app.route("/", methods=["GET", "POST"])
def index():
    results = []

    if request.method == "POST":
        grocery_input = request.form.get("groceries", "")
        groceries = grocery_input.splitlines()
        results = count_groceries(groceries)

    return render_template("index.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)
