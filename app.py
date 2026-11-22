"""
Restaurant Ordering Bot - Streamlit UI (Problem 12)
Run with:  streamlit run app.py
"""

import streamlit as st
from ordering_bot import load_menu, take_order

st.set_page_config(page_title="Restaurant Ordering Bot", page_icon="🍽️")

menu = load_menu()

st.title("🍽️ Restaurant Ordering Bot")
st.caption("Type your order in plain English. Powered by a local LLM (Ollama · llama3.1).")

# ---- Sidebar: show the menu ----
with st.sidebar:
    st.header("📋 Menu")
    categories = {}
    for name, info in menu.items():
        categories.setdefault(info["category"], []).append((name, info["price"]))
    for cat, items in categories.items():
        st.subheader(cat)
        for name, price in items:
            st.write(f"- {name} — ₹{int(price)}")

# ---- Main input ----
st.write("#### What would you like to order?")
examples = [
    "2 margherita pizzas and a cold coffee",
    "one chicken biryani, 3 gulab jamun and a mango lassi",
    "I'll have a veg burger, fries and a sushi roll please",
]
example = st.selectbox("Try an example (optional):", [""] + examples)
user_text = st.text_area("Your order:", value=example, height=100,
                         placeholder="e.g. 2 veg burgers and a cold coffee")

if st.button("🧾 Place Order", type="primary"):
    if not user_text.strip():
        st.warning("Please type an order first.")
    else:
        with st.spinner("Reading your order..."):
            try:
                order, bill = take_order(user_text, menu)
            except Exception as e:
                st.error(f"Could not reach the model: {e}")
                st.stop()

        if bill["line_items"]:
            st.success("Order confirmed! Here is your bill:")
            st.table(
                [
                    {
                        "Item": li["name"],
                        "Qty": li["qty"],
                        "Price (₹)": int(li["price"]),
                        "Total (₹)": int(li["line_total"]),
                    }
                    for li in bill["line_items"]
                ]
            )
            c1, c2, c3 = st.columns(3)
            c1.metric("Subtotal", f"₹{bill['subtotal']:.2f}")
            c2.metric("Tax (5%)", f"₹{bill['tax']:.2f}")
            c3.metric("TOTAL", f"₹{bill['total']:.2f}")
        else:
            st.warning("No valid menu items were found in your order.")

        if bill["unavailable"]:
            st.info("Not on our menu: " + ", ".join(bill["unavailable"]))

        with st.expander("🔍 Raw JSON extracted by the LLM"):
            st.json(order)
