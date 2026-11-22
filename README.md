# Problem 12 — Restaurant Ordering Bot


---

## 1. Problem Understanding

Taking restaurant orders by phone is slow and error-prone — staff mishear items,
forget quantities, and make mistakes adding up the bill. This project builds a
**chatbot that shows a menu, takes an order typed in plain English, and confirms
the bill automatically.**

The key design decision: **the LLM is used only to understand language, never to do
arithmetic.** The model reads the customer's sentence and extracts *which items* and
*how many* as structured JSON. Plain Python then looks up prices and calculates the
bill. This keeps the money math 100% correct even if the model is imperfect.

```
Menu (CSV)  ──►  System prompt with menu  ──►  LLM extracts items+qty as JSON
                                                        │
                                                        ▼
                              Python looks up prices & calculates the bill
```

## 2. Prompt Design

The system prompt (built in `ordering_bot.py → build_system_prompt`):

1. Injects the **full menu with prices** so the model can only choose real items.
2. Instructs the model to **match each request to the exact menu name**.
3. Handles edge cases: default quantity = 1, and items not on the menu go into an
   `"unavailable"` list instead of being invented.
4. Forces a **strict JSON output shape** — and Ollama is called with `format: "json"`
   and `temperature: 0` so the output is valid, deterministic JSON every time.

```json
{
  "items": [{"name": "Margherita Pizza", "quantity": 2}],
  "unavailable": ["sushi roll"]
}
```

## 3. Implementation

| File | Purpose |
|------|---------|
| `menu.csv` | Menu with prices & categories (18 items) |
| `ordering_bot.py` | Core logic: load menu → build prompt → call LLM → **calculate bill** |
| `app.py` | Streamlit UI (menu sidebar, order box, receipt table) |
| `test_samples.py` | Automated test on 6 sample inputs |
| `requirements.txt` | Dependencies |

**Model:** `llama3.1` running **locally via Ollama** — no API key, no cost, works offline.
The code reads `OLLAMA_MODEL` / `OLLAMA_URL` env vars, so it can be pointed at any
Ollama model (e.g. `qwen3:4b`) without code changes.

## 4. How to Run

```bash
# 1. make sure Ollama is running and the model is present
ollama pull llama3.1
ollama serve        # usually already running

# 2. install python deps
pip install -r requirements.txt

# 3a. run the automated tests (CLI)
python3 test_samples.py

# 3b. run the web UI (Streamlit — needs `pip install streamlit`)
streamlit run app.py

# 3c. OR run the zero-install web UI (no pip needed, standard library only)
python3 app_web.py        # then open http://localhost:7860
```

> **Note:** `app_web.py` is a fallback UI that uses only Python's standard library,
> so it runs even on a machine where you can't install Streamlit. Same features.

## 5. Testing on Sample Inputs

Tested on **6 sample orders** (`test_samples.py`, full output in `test_output.txt`):

| # | Input | What it checks | Result |
|---|-------|----------------|--------|
| 1 | "2 margherita pizzas and a cold coffee" | basic multi-item + quantity | ✅ ₹567.00 |
| 2 | "one chicken biryani, 3 gulab jamun and a mango lassi" | number words + digits mixed | ✅ ₹588.00 |
| 3 | "veg burger, fries and a **sushi roll**" | item not on menu → `unavailable` | ✅ sushi flagged, ₹210.00 |
| 4 | "give me **five** masala chai" | spelled-out quantity | ✅ 5 × chai, ₹210.00 |
| 5 | "paneer butter masala with garlic bread and a fresh lime soda" | fuzzy phrasing → exact names | ✅ ₹420.00 |
| 6 | "nothing fancy, just a chocolate brownie" | noise words ignored | ✅ ₹126.00 |

**All 6 passed.** The bot correctly parsed quantities (digits and words), matched
casual phrasing to exact menu names, rejected off-menu items, and computed every bill
(subtotal + 5% GST) correctly.

## 6. Limitations & Possible Extensions

- Currently one-shot (no multi-turn "add fries to that"). Could keep conversation state.
- Fuzzy matching relies on the LLM; a very unusual nickname could be missed.
- Could add order persistence, a "modify/cancel" flow, or payment confirmation.

---
*Stack: Python · Streamlit · Ollama (llama3.1, local) — no model training required.*
