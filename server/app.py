from flask import Flask, render_template, request, send_from_directory
from server.database.connection import SessionLocal
from server.database.models import ProductPrice
from collections import defaultdict

# Import scheduler
from server.scheduler.run_scheduler import start_scheduler  

# ✅ Start scheduler when Flask boots up
start_scheduler()
 
app = Flask(__name__, template_folder="../client/templates", static_folder="../client/static")

# ✅ Start scheduler when Flask boots up
start_scheduler()

def fix_link(source_name):
    """Generate proper links for each source"""
    source_lower = source_name.lower().replace(" ", "")
    if "osusu" in source_lower:
        return "https://pro.packnpay.com.ng"
    elif "pricepally" in source_lower:
        return "https://pricepally.com"
    elif "market" in source_lower or "food" in source_lower:
        return "https://themarketfoodshop.com/"
    else:
        return f"https://{source_lower}.com"

@app.route("/", methods=["GET"])
def home():
    query = request.args.get("q")
    products = []

    if query:
        session = SessionLocal()
        try:
            db_query = session.query(ProductPrice).filter(ProductPrice.product_name.ilike(f"%{query}%")).all()
            
            product_dict = defaultdict(lambda: defaultdict(list))
            for row in db_query:
                price_to_use = row.detail if row.source and "pricepally" in row.source.lower().replace(" ", "") else row.price

                if price_to_use is not None:
                    product_dict[row.product_name][row.source].append({
                        "price": price_to_use,
                        "detail": row.detail,
                        "link": fix_link(row.source),
                        "image": "/static/images/placeholder.png"
                    })

            for name, sources_dict in product_dict.items():
                sources_list = []
                for source_name, price_list in sources_dict.items():
                    if price_list:
                        raw_price = price_list[0]["price"]
                        price_display = "N/A"

                        if raw_price is not None:
                            cleaned_price = str(raw_price).replace("₦", "").replace(",", "").strip()
                            try:
                                if " - " in cleaned_price:
                                    price_parts = cleaned_price.split(" - ")
                                    min_price = float(price_parts[0])
                                    max_price = float(price_parts[1])
                                    price_display = f"₦{min_price:,.0f} - ₦{max_price:,.0f}"
                                else:
                                    price_display = f"₦{float(cleaned_price):,.0f}"
                            except (ValueError, TypeError, IndexError):
                                price_display = "N/A"

                        sources_list.append({
                            "source": source_name,
                            "price": price_display,
                            "detail": price_list[0]["detail"],
                            "link": fix_link(source_name),
                            "image": price_list[0]["image"]
                        })
                
                products.append({
                    "name": name,
                    "sources": sources_list
                })

        finally:
            session.close()

    return render_template("index.html", products=products, query=query)

# ✅ New route to serve sitemap.xml
@app.route("/sitemap.xml", methods=["GET"])
def sitemap():
    return send_from_directory(app.static_folder, "sitemap.xml")

if __name__ == "__main__":
    app.run(debug=True)
