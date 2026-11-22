"""
Restaurant Ordering Bot - core logic (Problem 12)
--------------------------------------------------
Flow:  menu (CSV) -> system prompt with menu -> LLM extracts items + quantity
       as JSON -> Python calculates the bill.

Uses a local Ollama model (llama3.1) so no API key is needed.
"""

import csv
import json
import os
import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434/api/chat")
MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:latest")
MENU_FILE = os.path.join(os.path.dirname(__file__), "menu.csv")
TAX_RATE = 0.05  # 5% GST on the food total


# ---------------------------------------------------------------------------
# 1. Load the menu from CSV into a dict {item_name: price}
# ---------------------------------------------------------------------------
def load_menu(path=MENU_FILE):
    menu = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            menu[row["item"].strip()] = {
                "price": float(row["price"]),
                "category": row["category"].strip(),
            }
    return menu


# ---------------------------------------------------------------------------
# 2. Build the system prompt that contains the menu
# ---------------------------------------------------------------------------
def build_system_prompt(menu):
    menu_lines = "\n".join(
        f"- {name} (Rs.{int(info['price'])})" for name, info in menu.items()
    )
    return f"""You are an order-taking assistant for a restaurant.

Here is the ONLY menu you can take orders from:
{menu_lines}

The customer will type their order in plain English.
Your job: extract the ordered items and their quantities.

Rules:
- Match each requested item to the CLOSEST menu item name EXACTLY as written above.
- If the customer asks for something not on the menu, add its name to "unavailable".
- If no quantity is given, assume 1.
- Respond with ONLY a JSON object, no extra text, in exactly this shape:

{{
  "items": [
    {{"name": "<exact menu item name>", "quantity": <integer>}}
  ],
  "unavailable": ["<item the customer asked for that is not on the menu>"]
}}
"""


# ---------------------------------------------------------------------------
# 3. Call the LLM (Ollama) and get back JSON
# ---------------------------------------------------------------------------
def extract_order(user_text, menu, timeout=120):
    system_prompt = build_system_prompt(menu)
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text},
        ],
        "format": "json",   # ask Ollama to return valid JSON
        "stream": False,
        "options": {"temperature": 0},
    }
    resp = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
    resp.raise_for_status()
    content = resp.json()["message"]["content"]
    data = json.loads(content)

    # normalise shape so the rest of the code is safe
    data.setdefault("items", [])
    data.setdefault("unavailable", [])
    return data


# ---------------------------------------------------------------------------
# 4. Python calculates the bill (never trust the LLM with math)
# ---------------------------------------------------------------------------
def calculate_bill(order, menu):
    line_items = []
    subtotal = 0.0
    not_found = list(order.get("unavailable", []))

    for entry in order.get("items", []):
        name = entry.get("name", "").strip()
        qty = int(entry.get("quantity", 1) or 1)

        if name in menu:
            price = menu[name]["price"]
            line_total = price * qty
            subtotal += line_total
            line_items.append(
                {"name": name, "qty": qty, "price": price, "line_total": line_total}
            )
        else:
            not_found.append(name)

    tax = round(subtotal * TAX_RATE, 2)
    total = round(subtotal + tax, 2)
    return {
        "line_items": line_items,
        "subtotal": round(subtotal, 2),
        "tax": tax,
        "total": total,
        "unavailable": [x for x in not_found if x],
    }


# ---------------------------------------------------------------------------
# 5. Pretty-print a receipt (used by CLI + tests)
# ---------------------------------------------------------------------------
def format_receipt(bill):
    lines = ["------ ORDER RECEIPT ------"]
    for li in bill["line_items"]:
        lines.append(
            f"{li['qty']} x {li['name']:<22} Rs.{li['line_total']:.2f}"
        )
    if not bill["line_items"]:
        lines.append("(no valid items)")
    lines.append("---------------------------")
    lines.append(f"Subtotal                 Rs.{bill['subtotal']:.2f}")
    lines.append(f"Tax (5% GST)             Rs.{bill['tax']:.2f}")
    lines.append(f"TOTAL                    Rs.{bill['total']:.2f}")
    if bill["unavailable"]:
        lines.append("")
        lines.append("Not available: " + ", ".join(bill["unavailable"]))
    lines.append("---------------------------")
    return "\n".join(lines)


def take_order(user_text, menu=None):
    """Convenience: text in -> (order_json, bill) out."""
    menu = menu or load_menu()
    order = extract_order(user_text, menu)
    bill = calculate_bill(order, menu)
    return order, bill


# ---------------------------------------------------------------------------
# CLI entry point for a quick manual test
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    menu = load_menu()
    print("Restaurant Ordering Bot (type 'quit' to exit)\n")
    while True:
        text = input("Your order> ").strip()
        if text.lower() in {"quit", "exit", "q"}:
            break
        order, bill = take_order(text, menu)
        print("\nExtracted JSON:", json.dumps(order, indent=2))
        print(format_receipt(bill), "\n")
