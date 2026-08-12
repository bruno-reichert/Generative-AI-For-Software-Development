from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import ForeignKey, String, Numeric, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# 1. Create a Base class that all our table classes will inherit from
class Base(DeclarativeBase):
    pass

# =====================================================================
# Table 1: Users
# =====================================================================
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationship: A user can have many orders
    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")


# =====================================================================
# Table 2: Products
# =====================================================================
class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    # Numeric is preferred over Float for money to prevent rounding errors
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(default=0)

    # Relationship: A product can be in many order items
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")


# =====================================================================
# Table 3: Orders
# =====================================================================
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Foreign Key linking this order back to a specific user
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


# =====================================================================
# Table 4: Order Items (The Bridge Table)
# =====================================================================
class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Links to the parent order
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    # Links to the product being purchased
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    
    # Crucial E-commerce Rule: Store the price at the exact moment of purchase. 
    # If the product's price changes in the "products" table later, historical 
    # invoices must remain unchanged.
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")