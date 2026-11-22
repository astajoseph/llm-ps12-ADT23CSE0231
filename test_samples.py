"""
Test the Restaurant Ordering Bot on sample inputs (Problem 12).
Run with:  python3 test_samples.py
Prints the extracted JSON and the calculated bill for each sample.
"""

import json
from ordering_bot import load_menu, take_order, format_receipt

SAMPLES = [
    "2 margherita pizzas and a cold coffee",
    "one chicken biryani, 3 gulab jamun and a mango lassi",
    "I'll have a veg burger, fries and a sushi roll please",   # sushi = not on menu
    "give me five masala chai",
    "paneer butter masala with garlic bread and a fresh lime soda",
    "nothing fancy, just a chocolate brownie",
]


def main():
    menu = load_menu()
    for i, text in enumerate(SAMPLES, 1):
        print("=" * 50)
        print(f"SAMPLE {i}: {text}")
        print("-" * 50)
        order, bill = take_order(text, menu)
        print("Extracted JSON:")
        print(json.dumps(order, indent=2))
        print(format_receipt(bill))
        print()


if __name__ == "__main__":
    main()
