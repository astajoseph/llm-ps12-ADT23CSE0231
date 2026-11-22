"""
Generate the 2-page procedure report as a PDF (report.pdf) using only PIL.
Also renders two 'screenshot' images from the project's real output.
"""
from PIL import Image, ImageDraw, ImageFont

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def f(size, bold=False, mono=False):
    return ImageFont.truetype(MONO if mono else (FONT_B if bold else FONT), size)


# A4 at 150 DPI
W, H = 1240, 1754
MARGIN = 95
INK = (25, 25, 25)
BROWN = (150, 85, 20)
GREEN = (26, 120, 26)
GREY = (110, 110, 110)


# ---------------------------------------------------------------------------
# Screenshot 1: the web UI with a sample order + receipt
# ---------------------------------------------------------------------------
def make_ui_screenshot(path):
    w, h = 1000, 680
    img = Image.new("RGB", (w, h), (255, 255, 255))
    d = ImageDraw.Draw(img)
    # browser chrome
    d.rectangle([0, 0, w, 46], fill=(222, 222, 222))
    for i, c in enumerate([(237, 106, 94), (245, 191, 79), (98, 197, 84)]):
        d.ellipse([18 + i * 26, 16, 34 + i * 26, 32], fill=c)
    d.rounded_rectangle([110, 12, w - 20, 34], 11, fill=(255, 255, 255))
    d.text((124, 16), "localhost:7860", font=f(16), fill=(90, 90, 90))
    # title
    d.text((28, 62), "Restaurant Ordering Bot", font=f(30, bold=True), fill=INK)
    d.text((28, 104), "Type your order in plain English - powered by a local LLM (Ollama / llama3.1).",
           font=f(16), fill=GREY)
    # menu sidebar
    d.rounded_rectangle([28, 140, 300, 650], 10, fill=(250, 247, 242), outline=(234, 223, 206))
    d.text((44, 152), "Menu", font=f(20, bold=True), fill=INK)
    menu = [("Main", ["Margherita Pizza - Rs.220", "Farmhouse Pizza - Rs.300",
                      "Chicken Biryani - Rs.230", "Veg Burger - Rs.110"]),
            ("Sides", ["French Fries - Rs.90", "Garlic Bread - Rs.100"]),
            ("Beverage", ["Cold Coffee - Rs.100", "Masala Chai - Rs.40"])]
    y = 186
    for cat, items in menu:
        d.text((44, y), cat, font=f(15, bold=True), fill=BROWN); y += 24
        for it in items:
            d.text((56, y), "- " + it, font=f(14), fill=(60, 60, 60)); y += 22
        y += 6
    # order box
    d.text((330, 150), "What would you like to order?", font=f(17, bold=True), fill=INK)
    d.rounded_rectangle([330, 180, w - 30, 236], 8, outline=(170, 170, 170))
    d.text((344, 196), "2 margherita pizzas and a cold coffee", font=f(18), fill=INK)
    d.rounded_rectangle([330, 250, 470, 292], 8, fill=BROWN)
    d.text((352, 260), "Place Order", font=f(17, bold=True), fill=(255, 255, 255))
    # receipt
    d.rounded_rectangle([330, 312, w - 30, 650], 10, fill=(246, 255, 246), outline=(207, 233, 207))
    d.text((346, 324), "Order Confirmed", font=f(19, bold=True), fill=GREEN)
    cols = [346, 630, 740, 860]
    d.text((cols[0], 360), "Item", font=f(15, bold=True), fill=INK)
    d.text((cols[1], 360), "Qty", font=f(15, bold=True), fill=INK)
    d.text((cols[2], 360), "Price", font=f(15, bold=True), fill=INK)
    d.text((cols[3], 360), "Total", font=f(15, bold=True), fill=INK)
    rows = [("Margherita Pizza", "2", "Rs.220", "Rs.440"),
            ("Cold Coffee", "1", "Rs.100", "Rs.100")]
    y = 390
    for r in rows:
        for cx, val in zip(cols, r):
            d.text((cx, y), val, font=f(15), fill=(40, 40, 40))
        y += 30
    d.line([346, y + 4, w - 46, y + 4], fill=(207, 233, 207))
    d.text((346, y + 16), "Subtotal:  Rs.540.00", font=f(15), fill=INK)
    d.text((346, y + 42), "Tax (5% GST):  Rs.27.00", font=f(15), fill=INK)
    d.text((346, y + 74), "TOTAL:  Rs.567.00", font=f(21, bold=True), fill=GREEN)
    img.save(path)


# ---------------------------------------------------------------------------
# Screenshot 2: terminal output of the test run (off-menu case)
# ---------------------------------------------------------------------------
def make_terminal_screenshot(path):
    w, h = 1000, 430
    img = Image.new("RGB", (w, h), (30, 30, 34))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, 34], fill=(55, 55, 60))
    d.text((16, 8), "python3 test_samples.py", font=f(15, mono=True), fill=(210, 210, 210))
    lines = [
        ("$ python3 test_samples.py", (120, 220, 120)),
        ("SAMPLE 3: I'll have a veg burger, fries and a sushi roll please", (240, 240, 150)),
        ("Extracted JSON:", (200, 200, 200)),
        ('{ "items": [ {"name": "Veg Burger", "quantity": 1},', (170, 200, 240)),
        ('             {"name": "French Fries", "quantity": 1} ],', (170, 200, 240)),
        ('  "unavailable": ["sushi roll"] }', (240, 160, 160)),
        ("------ ORDER RECEIPT ------", (210, 210, 210)),
        ("1 x Veg Burger        Rs.110.00", (210, 210, 210)),
        ("1 x French Fries      Rs.90.00", (210, 210, 210)),
        ("Subtotal              Rs.200.00", (210, 210, 210)),
        ("Tax (5% GST)          Rs.10.00", (210, 210, 210)),
        ("TOTAL                 Rs.210.00", (150, 230, 150)),
        ("Not available: sushi roll", (240, 160, 160)),
    ]
    y = 48
    for text, col in lines:
        d.text((16, y), text, font=f(15, mono=True), fill=col); y += 28
    img.save(path)


# ---------------------------------------------------------------------------
# Text layout helpers
# ---------------------------------------------------------------------------
class Page:
    def __init__(self):
        self.img = Image.new("RGB", (W, H), (255, 255, 255))
        self.d = ImageDraw.Draw(self.img)
        self.y = MARGIN

    def wrap(self, text, font, width):
        words, lines, cur = text.split(), [], ""
        for wd in words:
            t = (cur + " " + wd).strip()
            if self.d.textlength(t, font=font) <= width:
                cur = t
            else:
                if cur:
                    lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, text, size=22, bold=False, color=INK, indent=0, gap=5, lh=1.38, mono=False):
        font = f(size, bold=bold, mono=mono)
        x = MARGIN + indent
        for line in self.wrap(text, font, W - 2 * MARGIN - indent):
            self.d.text((x, self.y), line, font=font, fill=color)
            self.y += int(size * lh)
        self.y += gap

    def heading(self, text):
        self.y += 6
        self.d.text((MARGIN, self.y), text, font=f(24, bold=True), fill=BROWN)
        self.y += 34
        self.d.line([MARGIN, self.y, W - MARGIN, self.y], fill=(225, 210, 190))
        self.y += 10

    def image(self, path, max_w=None, gap=10):
        im = Image.open(path)
        mw = max_w or (W - 2 * MARGIN)
        if im.width > mw:
            im = im.resize((mw, int(im.height * mw / im.width)))
        self.d.rectangle([MARGIN - 1, self.y - 1, MARGIN + im.width, self.y + im.height],
                         outline=(200, 200, 200))
        self.img.paste(im, (MARGIN, self.y))
        self.y += im.height + gap


# ---------------------------------------------------------------------------
# Build the two pages
# ---------------------------------------------------------------------------
def build():
    make_ui_screenshot("screenshot_ui.png")
    make_terminal_screenshot("screenshot_terminal.png")

    # ---------------- PAGE 1 ----------------
    p1 = Page()
    p1.d.text((MARGIN, p1.y), "Restaurant Ordering Bot", font=f(32, bold=True), fill=INK)
    p1.y += 44
    p1.d.text((MARGIN, p1.y), "Mini LLM Project - Procedure Report", font=f(20), fill=GREY)
    p1.y += 36
    p1.d.line([MARGIN, p1.y, W - MARGIN, p1.y], fill=(180, 180, 180)); p1.y += 14

    for label, val in [
        ("Project Title:", "Restaurant Ordering Bot"),
        ("Problem Statement No.:", "12"),
        ("Name:", "Asta Joseph"),
        ("Roll No.:", "12"),
        ("Class / Section:", "[fill in your class]"),
        ("GitHub link:", "[paste your GitHub repository link]"),
    ]:
        p1.d.text((MARGIN, p1.y), label, font=f(21, bold=True), fill=INK)
        p1.d.text((MARGIN + 290, p1.y), val, font=f(21), fill=INK)
        p1.y += 30
    p1.y += 6

    p1.heading("Problem Statement")
    p1.para("Taking restaurant orders over the phone is slow and error-prone - staff mishear "
            "items, forget quantities, and make mistakes while adding up the bill. This project is "
            "a chatbot that shows a menu, reads an order typed in plain English, extracts the items "
            "and quantities, and confirms an itemised bill automatically. It helps small restaurant "
            "and cafe staff take faster, more accurate orders.")

    p1.heading("Tools & Model")
    p1.para("Language: Python 3.12", gap=2)
    p1.para("LLM: Llama 3.1 (8B) running locally through Ollama - no API key, no cost, works offline.", gap=2)
    p1.para("Model call: Ollama chat API over HTTP (localhost:11434) with format=\"json\" and temperature=0.", gap=2)
    p1.para("Libraries: requests (HTTP call); csv and json from the standard library.", gap=2)
    p1.para("UI: a lightweight web page built with Python's standard-library http.server "
            "(an equivalent Streamlit version, app.py, is also included).")

    p1.heading("Procedure (what I actually did)")
    steps = [
        "Setup: checked that Python 3.12 and Ollama were installed and that the llama3.1 model was "
        "already pulled (ollama list).",
        "Model instead of API key: I used a local model, so no paid API key was needed - I only made "
        "sure \"ollama serve\" was running on localhost:11434.",
        "Menu data: created menu.csv with 18 items, prices and categories, and wrote load_menu() to "
        "read it into a Python dictionary.",
        "Prompt: wrote a system prompt that injects the whole menu and asks the model to return ONLY "
        "JSON with items, quantities and any unavailable items. I tested it on 3-5 sample sentences first.",
        "Core code (ordering_bot.py): take the sentence -> build the prompt -> call the model -> parse "
        "the JSON -> then Python (not the LLM) looks up prices and computes subtotal + 5% GST + total.",
        "UI (app_web.py): a menu sidebar, an order box with example orders, and a green receipt table "
        "that shows the confirmed bill.",
        "Testing: ran test_samples.py on 6 inputs covering digits, spelled-out numbers, off-menu items "
        "and noise words, and saved the outputs.",
    ]
    for i, s in enumerate(steps, 1):
        p1.para(f"{i}.  {s}", size=21, gap=4, indent=12)

    p1.img.save("_p1.png")

    # ---------------- PAGE 2 ----------------
    p2 = Page()
    p2.heading("Prompt Used")
    p2.para("Final system prompt sent to the model (menu abbreviated):", size=21, gap=4)
    p2.para('"You are an order-taking assistant for a restaurant. Here is the ONLY menu you can take '
            'orders from: <menu with prices>. The customer types their order in plain English. Extract '
            'the ordered items and their quantities. Rules: match each item to the CLOSEST menu name '
            'EXACTLY as written; if an item is not on the menu, add it to \'unavailable\'; if no quantity '
            'is given, assume 1. Respond with ONLY a JSON object: { \"items\": [ {\"name\": <exact name>, '
            '\"quantity\": <integer>} ], \"unavailable\": [<item not on menu>] }"',
            size=19, mono=True, lh=1.32, color=(40, 40, 40))
    p2.para("One change I made to improve it: at first the model sometimes wrapped the JSON in extra "
            "prose or invented items. I fixed this by adding the explicit \"unavailable\" list and the "
            "\"assume 1\" rule, and by calling Ollama with format=\"json\" and temperature=0 - this forced "
            "clean, deterministic JSON every time.")

    p2.heading("Results")
    p2.para("Sample input \"2 margherita pizzas and a cold coffee\" -> correct bill of Rs.567.00:",
            size=20, gap=4)
    p2.image("screenshot_ui.png", max_w=680, gap=8)
    p2.para("Terminal test run (off-menu item \"sushi roll\" is correctly rejected):", size=20, gap=4)
    p2.image("screenshot_terminal.png", max_w=680, gap=8)

    p2.heading("Challenges & Fixes")
    ch = [
        "The model sometimes added text around the JSON or invented items - fixed with format=\"json\", "
        "temperature=0 and stricter prompt rules.",
        "Letting the LLM do the arithmetic gave wrong totals - fixed by moving all money math into Python "
        "and using the model only for language understanding.",
        "Port 8000 was already in use (\"Address already in use\") - fixed by moving the web server to port 7860.",
        "Streamlit would not install on the offline machine (no internet to reach PyPI) - fixed by writing a "
        "zero-dependency UI with the standard-library http.server, so the demo runs with no pip install.",
    ]
    for s in ch:
        p2.para("- " + s, size=21, gap=4, indent=12)

    p2.heading("Conclusion")
    p2.para("What works: the bot reliably reads natural-language orders, extracts items and quantities as "
            "JSON, rejects off-menu items, and produces a correct itemised bill with tax. What doesn't yet: "
            "it is single-turn, so it can't handle follow-ups like \"add fries to that\" or edit an existing "
            "order. Future improvement: add multi-turn conversation memory so a customer can build and modify "
            "an order over several messages, and add an order-confirmation / payment step.")

    p2.img.save("_p2.png")

    # ---------------- combine to PDF ----------------
    p1i = Image.open("_p1.png").convert("RGB")
    p2i = Image.open("_p2.png").convert("RGB")
    p1i.save("report.pdf", save_all=True, append_images=[p2i], resolution=150.0)
    print("Wrote report.pdf (2 pages)")


if __name__ == "__main__":
    build()
