from datetime import datetime
from decimal import Decimal
from typing import List
from sqlalchemy import create_engine, ForeignKey, String, Numeric, DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

# =====================================================================
# 1. Initialize the Database Engine
# =====================================================================
engine = create_engine("sqlite:///ecommerce.db", echo=True)


# =====================================================================
# 2. Define the Schema Structure
# =====================================================================
class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(default=0)

    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="pending")

    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


# =====================================================================
# 3. Create the Tables in the Database
# =====================================================================
if __name__ == "__main__":
    print("\n--- Generating Database Tables ---")
    
    # This command reads all classes inheriting from Base and builds them in order
    Base.metadata.create_all(engine)
    
    print("\n--- Generation Complete! ---")