import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order, NewsletterSubscriber, BlogPost

app = FastAPI(title="STOUSH API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Utility
class IdModel(BaseModel):
    id: str


def oid(id_str: str) -> ObjectId:
    try:
        return ObjectId(id_str)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid id")


@app.get("/")
def root():
    return {"brand": "STOUSH", "tagline": "Start Something"}


# Catalog
@app.get("/products", response_model=List[Product])
def list_products(category: Optional[str] = None, featured: Optional[bool] = None):
    q: dict = {}
    if category:
        q["category"] = category
    if featured is not None:
        q["featured"] = featured
    items = get_documents("product", q)
    for it in items:
        it.pop("_id", None)
    return items


@app.get("/products/{handle}", response_model=Product)
def get_product(handle: str):
    docs = get_documents("product", {"handle": handle})
    if not docs:
        raise HTTPException(status_code=404, detail="Product not found")
    doc = docs[0]
    doc.pop("_id", None)
    return doc


@app.post("/products", response_model=IdModel)
def create_product(p: Product):
    new_id = create_document("product", p)
    return {"id": new_id}


# Newsletter
@app.post("/newsletter", response_model=IdModel)
def subscribe(n: NewsletterSubscriber):
    new_id = create_document("newslettersubscriber", n)
    return {"id": new_id}


# Orders (placeholder create; payment handled client-side with Stripe/PayPal SDKs)
@app.post("/orders", response_model=IdModel)
def create_order(order: Order):
    new_id = create_document("order", order)
    return {"id": new_id}


# Shipping calculator (simple flat-rate example; replace with real rates later)
class ShippingQuote(BaseModel):
    country: str
    subtotal: float
    shipping: float
    currency: str = "AUD"

@app.get("/shipping/calc", response_model=ShippingQuote)
def calc_shipping(country: str = "AU", subtotal: float = 0.0):
    country = country.upper()
    if country == "AU":
        shipping = 0.0 if subtotal >= 150 else 9.99
    else:
        shipping = 0.0 if subtotal >= 300 else 24.99
    return ShippingQuote(country=country, subtotal=subtotal, shipping=shipping)


# Blog basic endpoints
@app.get("/blog", response_model=List[BlogPost])
def list_posts():
    posts = get_documents("blogpost", {"published": True})
    for p in posts:
        p.pop("_id", None)
    return posts

@app.post("/blog", response_model=IdModel)
def create_post(post: BlogPost):
    new_id = create_document("blogpost", post)
    return {"id": new_id}


@app.get("/test")
def test_database():
    resp = {
        "backend": "running",
        "database": "not connected",
        "collections": []
    }
    try:
        if db is not None:
            resp["database"] = "connected"
            resp["collections"] = db.list_collection_names()[:10]
    except Exception as e:
        resp["database"] = f"error: {str(e)[:60]}"
    resp["database_url"] = "set" if os.getenv("DATABASE_URL") else "not set"
    resp["database_name"] = "set" if os.getenv("DATABASE_NAME") else "not set"
    return resp


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
