"""
Database Schemas for STOUSH

Each Pydantic model represents a MongoDB collection. The collection name is the
lowercased class name (e.g., Product -> "product").
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal
from datetime import datetime

# Core domain models

class Variant(BaseModel):
    sku: str = Field(..., description="Unique SKU")
    size: Literal["XS","S","M","L","XL","XXL"] = Field(..., description="Size option")
    color: Optional[str] = Field(None, description="Color name if applicable")
    price: float = Field(..., ge=0, description="Price in AUD")
    stock: int = Field(..., ge=0, description="Inventory count")

class Image(BaseModel):
    url: HttpUrl
    alt: Optional[str] = None

class Product(BaseModel):
    title: str
    handle: str = Field(..., description="URL-friendly unique handle")
    description: Optional[str] = None
    category: Literal["Training","Street","Drops"]
    tags: List[str] = []
    featured: bool = False
    hero: bool = False
    images: List[Image] = []
    variants: List[Variant] = []
    materials: Optional[str] = None
    care: Optional[str] = None
    low_stock_threshold: int = 5
    published: bool = True

class CartItem(BaseModel):
    product_id: str
    sku: str
    qty: int = Field(..., ge=1, le=10)
    price: float = Field(..., ge=0)
    title: str
    size: Optional[str] = None
    image: Optional[HttpUrl] = None

class Order(BaseModel):
    email: str
    items: List[CartItem]
    subtotal: float
    shipping: float
    total: float
    currency: Literal["AUD","USD"] = "AUD"
    status: Literal["created","paid","shipped","cancelled"] = "created"
    payment_provider: Optional[Literal["stripe","paypal"]] = None
    transaction_id: Optional[str] = None
    shipping_country: str = "AU"
    created_at: Optional[datetime] = None

class NewsletterSubscriber(BaseModel):
    email: str
    source: Literal["hero","footer","modal","account"] = "hero"

class BlogPost(BaseModel):
    title: str
    slug: str
    excerpt: Optional[str] = None
    body: Optional[str] = None
    cover: Optional[HttpUrl] = None
    published: bool = True

class User(BaseModel):
    name: Optional[str] = None
    email: str
    password_hash: Optional[str] = None
    role: Literal["customer","admin"] = "customer"
