from collections import defaultdict

def parse_log(line: str) -> dict:
    parts = line.split("|")
    date = parts[0]

    data = {"date": date}
    for p in parts[1:]:
        key, value = p.split("=", 1)
        if key == "amount":
            value = int(value)
        data[key] = value

    return data

def calc_total_amount(logs: list[str]) -> int:
    total = 0
    for line in logs:
        total += parse_log(line)["amount"]
    return total


def calc_action_counts(logs: list[str]) -> dict:
    counts = defaultdict(int)
    for line in logs:
        action = parse_log(line)["action"]
        counts[action] += 1
    return dict(counts)


def calc_top2_users_by_amount(logs: list[str]) -> list[str]:
    totals = defaultdict(int)
    for line in logs:
        item = parse_log(line)
        totals[item["user"]] += item["amount"]
    top_users = sorted(totals.keys(), key=lambda u: totals[u], reverse=True)
    return top_users[:2]


def calc_date_with_max_turnover(logs: list[str]) -> str:
    by_date = defaultdict(int)
    for line in logs:
        item = parse_log(line)
        by_date[item["date"]] += item["amount"]

    return max(by_date.keys(), key=lambda d: by_date[d])


def build_result(logs: list[str]) -> dict:
    result = {}
    result["total_amount"] = calc_total_amount(logs)
    result["action_counts"] = calc_action_counts(logs)
    result["top_users"] = calc_top2_users_by_amount(logs)
    result["top_date"] = calc_date_with_max_turnover(logs)
    return result


if __name__ == "__main__":
    logs = [
        "2024-01-01|user=alice|action=buy|amount=100",
        "2024-01-01|user=bob|action=buy|amount=50",
        "2024-01-02|user=alice|action=refund|amount=20",
        "2024-01-02|user=carol|action=buy|amount=200",
        "2024-01-03|user=bob|action=buy|amount=150",
    ]

    result = build_result(logs)
    print(result)
