from collections import Counter


def main() -> None:
    for item, count in sorted(Counter(get_list()).items()):
        print(count, item)


def get_list() -> list[str]:
    groceries: list[str] = []
    while True:
        try:
            groceries.append(input().strip().upper())
        except EOFError:
            return groceries


if __name__ == "__main__":
    main()
