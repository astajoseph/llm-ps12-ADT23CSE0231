"""
Restaurant Ordering Bot - zero-dependency web UI (Problem 12)
-------------------------------------------------------------
A fallback UI that needs NO pip install (uses only Python's standard library).
Use this if you can't install Streamlit.

Run with:   python3 app_web.py
Then open:  http://localhost:7860
"""

import html
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from ordering_bot import load_menu, take_order

MENU = load_menu()
PORT = 7860

EXAMPLES = [
    "2 margherita pizzas and a cold coffee",
    "one chicken biryani, 3 gulab jamun and a mango lassi",
    "I'll have a veg burger, fries and a sushi roll please",
]


def menu_html():
    cats = {}
    for name, info in MENU.items():
        cats.setdefault(info["category"], []).append((name, info["price"]))
    out = []
    for cat, items in cats.items():
        out.append(f"<h4>{cat}</h4><ul>")
        for name, price in items:
            out.append(f"<li>{html.escape(name)} — ₹{int(price)}</li>")
        out.append("</ul>")
    return "".join(out)


def receipt_html(order, bill):
    rows = ""
    for li in bill["line_items"]:
        rows += (
            f"<tr><td>{html.escape(li['name'])}</td><td>{li['qty']}</td>"
            f"<td>₹{int(li['price'])}</td><td>₹{int(li['line_total'])}</td></tr>"
        )
    if not bill["line_items"]:
        rows = "<tr><td colspan='4'>No valid menu items found.</td></tr>"

    unavailable = ""
    if bill["unavailable"]:
        unavailable = ("<p class='note'>Not on our menu: "
                       + html.escape(", ".join(bill["unavailable"])) + "</p>")

    return f"""
    <div class="receipt">
      <h3>🧾 Order Confirmed</h3>
      <table>
        <tr><th>Item</th><th>Qty</th><th>Price</th><th>Total</th></tr>
        {rows}
      </table>
      <p>Subtotal: <b>₹{bill['subtotal']:.2f}</b></p>
      <p>Tax (5% GST): <b>₹{bill['tax']:.2f}</b></p>
      <p class="total">TOTAL: ₹{bill['total']:.2f}</p>
      {unavailable}
      <details><summary>Raw JSON from the LLM</summary>
        <pre>{html.escape(json.dumps(order, indent=2))}</pre>
      </details>
    </div>
    """


def page(order_text="", result_html=""):
    opts = "".join(f"<option>{html.escape(e)}</option>" for e in EXAMPLES)
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Restaurant Ordering Bot</title>
<style>
 body{{font-family:system-ui,Arial;max-width:900px;margin:30px auto;padding:0 16px;color:#222}}
 .layout{{display:flex;gap:30px;align-items:flex-start}}
 .menu{{flex:0 0 240px;background:#faf7f2;border:1px solid #eadfce;border-radius:10px;padding:12px 18px;font-size:14px}}
 .menu h4{{margin:10px 0 4px;color:#b5651d}} .menu ul{{margin:0 0 6px;padding-left:18px}}
 .main{{flex:1}}
 textarea{{width:100%;box-sizing:border-box;padding:10px;font-size:15px;border:1px solid #ccc;border-radius:8px}}
 button{{background:#b5651d;color:#fff;border:0;padding:10px 22px;font-size:15px;border-radius:8px;cursor:pointer;margin-top:8px}}
 select{{padding:6px;margin-bottom:8px}}
 table{{border-collapse:collapse;width:100%;margin:10px 0}}
 th,td{{border:1px solid #ddd;padding:6px 10px;text-align:left}}
 .receipt{{background:#f6fff6;border:1px solid #cfe9cf;border-radius:10px;padding:16px;margin-top:20px}}
 .total{{font-size:20px;font-weight:bold;color:#1a7f1a}}
 .note{{color:#b35}}
</style></head>
<body>
 <h1>🍽️ Restaurant Ordering Bot</h1>
 <p>Type your order in plain English — powered by a local LLM (Ollama · llama3.1).</p>
 <div class="layout">
   <div class="menu"><h2>📋 Menu</h2>{menu_html()}</div>
   <div class="main">
     <form method="POST" action="/">
       <label>Try an example:</label><br>
       <select onchange="document.getElementById('order').value=this.value">
         <option value="">-- pick one --</option>{opts}
       </select><br>
       <textarea id="order" name="order" rows="3"
         placeholder="e.g. 2 veg burgers and a cold coffee">{html.escape(order_text)}</textarea><br>
       <button type="submit">Place Order</button>
     </form>
     {result_html}
   </div>
 </div>
</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, body):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        self._send(page())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        fields = parse_qs(self.rfile.read(length).decode("utf-8"))
        order_text = fields.get("order", [""])[0].strip()
        result = ""
        if order_text:
            try:
                order, bill = take_order(order_text, MENU)
                result = receipt_html(order, bill)
            except Exception as e:
                result = f"<p class='note'>Error reaching the model: {html.escape(str(e))}</p>"
        self._send(page(order_text, result))

    def log_message(self, *args):  # keep the console quiet
        pass


if __name__ == "__main__":
    print(f"Restaurant Ordering Bot running at  http://localhost:{PORT}")
    print("Press Ctrl+C to stop.")
    HTTPServer(("0.0.0.0", PORT), Handler).serve_forever()
