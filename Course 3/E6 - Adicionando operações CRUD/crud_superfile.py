"""
E-Commerce Database Service Module
==================================
This module serves as a unified repository service for managing our e-commerce 
SQLite database. It encapsulates the SQLAlchemy engine, table schemas, 
and provides a complete transactional CRUD interface.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Sequence
from sqlalchemy import create_engine, ForeignKey, String, Numeric, DateTime, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

# =====================================================================
# 1. Database Initialization
# =====================================================================
# Initialize the engine. In production, this URI would be loaded from an environment variable.
engine = create_engine("sqlite:///ecommerce.db", echo=False)


# =====================================================================
# 2. Database Schemas (ORM Declarative Mapping)
# =====================================================================
class Base(DeclarativeBase):
    """Base class for all database model mappings."""
    pass


class User(Base):
    """Represents a customer in the system."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    # Relationship back-reference
    orders: Mapped[List["Order"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Product(Base):
    """Represents an item available in the inventory."""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    stock: Mapped[int] = mapped_column(default=0)

    # Relationship back-reference
    order_items: Mapped[List["OrderItem"]] = relationship(back_populates="product")


class Order(Base):
    """Represents a purchase transaction made by a User."""
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    status: Mapped[str] = mapped_column(String(20), default="pending")

    # Relationships
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    """Association table linking Orders to Products with historical purchase data."""
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Relationships
    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")


# =====================================================================
# 3. Create Schema Tables Utility
# =====================================================================
def initialize_tables():
    """Reads all schema definitions and creates the physical SQL tables in SQLite."""
    Base.metadata.create_all(engine)


# =====================================================================
# 4. CRUD: CREATE Operations
# =====================================================================
def create_user(session: Session, username: str, email: str) -> User:
    """
    Creates and commits a new User record in the database.

    :param session: Active SQLAlchemy database Session.
    :param username: Unique alphanumeric string representing the user.
    :param email: Unique email address string.
    :return: The created User object with its generated primary key ID.
    """
    new_user = User(username=username, email=email)
    session.add(new_user)
    session.commit()
    return new_user


def create_product(session: Session, name: str, price: float, stock: int) -> Product:
    """
    Creates and commits a new Product record in the database.

    :param session: Active SQLAlchemy database Session.
    :param name: Name of the product.
    :param price: Retail price of the product (float).
    :param stock: Initial inventory level (integer).
    :return: The created Product object with its generated primary key ID.
    """
    decimal_price = Decimal(str(price))
    new_product = Product(name=name, price=decimal_price, stock=stock)
    session.add(new_product)
    session.commit()
    return new_product


# =====================================================================
# 5. CRUD: READ (Querying) Operations
# =====================================================================
def get_user_by_id(session: Session, user_id: int) -> User | None:
    """
    Pulls a single User record from the database by its primary key ID.

    :param session: Active SQLAlchemy database Session.
    :param user_id: The primary key ID to search.
    :return: The User object if found, otherwise None.
    """
    return session.get(User, user_id)


def get_user_by_username(session: Session, username: str) -> User | None:
    """
    Searches and retrieves a User record by their unique username.

    :param session: Active SQLAlchemy database Session.
    :param username: The username string to filter by.
    :return: The User object if found, otherwise None.
    """
    query = select(User).where(User.username == username)
    return session.scalar(query)


def get_all_products(session: Session) -> Sequence[Product]:
    """
    Retrieves all products currently available in the database.

    :param session: Active SQLAlchemy database Session.
    :return: A list-like sequence of Product objects.
    """
    query = select(Product)
    return session.scalars(query).all()


# =====================================================================
# 6. CRUD: UPDATE Operations
# =====================================================================
def update_product_stock_and_price(session: Session, product_id: int, new_stock: int, new_price: float) -> Product | None:
    """
    Updates the stock and price values of an existing product using automatic dirty tracking.

    :param session: Active SQLAlchemy database Session.
    :param product_id: The primary key ID of the target product.
    :param new_stock: The updated inventory integer.
    :param new_price: The updated retail price float.
    :return: The updated Product object if found, otherwise None.
    """
    product = session.get(Product, product_id)
    if product:
        product.stock = new_stock
        product.price = Decimal(str(new_price))
        session.commit()
    return product


# =====================================================================
# 7. CRUD: DELETE Operations
# =====================================================================
def delete_product(session: Session, product_id: int) -> bool:
    """
    Deletes an existing product record from the database.

    :param session: Active SQLAlchemy database Session.
    :param product_id: The primary key ID of the target product.
    :return: True if the deletion succeeded, False if the product was not found.
    """
    product = session.get(Product, product_id)
    if product:
        session.delete(product)
        session.commit()
        return True
    return False