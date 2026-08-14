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

def create_order(session: Session, user_id: int, status: str = "pending") -> Order:
    """
    Creates and commits a new Order associated with a specific User.

    :param session: Active SQLAlchemy database Session.
    :param user_id: The primary key ID of the purchasing User.
    :param status: Initial order status string (defaults to 'pending').
    :return: The created Order object.
    :raises KeyError: If the user_id does not exist in the database.
    """
    # Defensive check: Ensure the purchasing user actually exists
    if not session.get(User, user_id):
        raise KeyError(f"Database Integrity Error: User with ID {user_id} does not exist.")

    new_order = Order(user_id=user_id, status=status)
    session.add(new_order)
    session.commit()
    return new_order


def add_item_to_order(session: Session, order_id: int, product_id: int, quantity: int) -> OrderItem:
    """
    Adds a product to an existing order, automatically snapshotting the product's 
    current retail price for historical purchase integrity.

    :param session: Active SQLAlchemy database Session.
    :param order_id: The primary key ID of the parent Order.
    :param product_id: The primary key ID of the Product being purchased.
    :param quantity: The number of units being purchased (integer).
    :return: The created OrderItem object.
    :raises KeyError: If the order_id or product_id does not exist in the database.
    """
    # Defensive check 1: Ensure the parent order actually exists
    if not session.get(Order, order_id):
        raise KeyError(f"Database Integrity Error: Order with ID {order_id} does not exist.")

    # Defensive check 2: Ensure the product actually exists, and retrieve it
    product = session.get(Product, product_id)
    if not product:
        raise KeyError(f"Database Integrity Error: Product with ID {product_id} does not exist.")

    # Automatically capture the product's current retail price at the exact moment of purchase
    new_item = OrderItem(
        order_id=order_id,
        product_id=product_id,
        quantity=quantity,
        price_at_purchase=product.price  # Dynamic price capture
    )
    
    session.add(new_item)
    session.commit()
    return new_item


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

def get_product_by_id(session: Session, product_id: int) -> Product | None:
    """
    Pulls a single Product record from the database by its primary key ID.

    :param session: Active SQLAlchemy database Session.
    :param product_id: The primary key ID of the target Product.
    :return: The Product object if found, otherwise None.
    """
    return session.get(Product, product_id)


def get_order_by_id(session: Session, order_id: int) -> Order | None:
    """
    Pulls a single Order record from the database by its primary key ID.

    :param session: Active SQLAlchemy database Session.
    :param order_id: The primary key ID of the target Order.
    :return: The Order object if found, otherwise None.
    """
    return session.get(Order, order_id)


def get_orders_by_user_id(session: Session, user_id: int) -> Sequence[Order]:
    """
    Retrieves the complete order history for a specific User.

    :param session: Active SQLAlchemy database Session.
    :param user_id: The primary key ID of the target User.
    :return: A list-like sequence of Order objects associated with the user.
    """
    query = select(Order).where(Order.user_id == user_id)
    return session.scalars(query).all()


def get_all_orders(session: Session) -> Sequence[Order]:
    """
    Retrieves all Orders registered in the system.

    :param session: Active SQLAlchemy database Session.
    :return: A list-like sequence of all Order objects.
    """
    query = select(Order)
    return session.scalars(query).all()

from sqlalchemy import func

def get_user_order_manifest(session: Session, user_id: int) -> List[dict]:
    """
    Retrieves a detailed manifest of everything a specific User has ordered.
    Displays what they bought, the quantities, and the prices.

    :param session: Active SQLAlchemy database Session.
    :param user_id: The primary key ID of the target User.
    :return: A list of dictionaries containing detailed purchase information.
    """
    # 1. Retrieve all orders associated with the user
    orders = get_orders_by_user_id(session, user_id)
    manifest = []

    # 2. Traverse the relationships (User -> Orders -> OrderItems -> Products)
    for order in orders:
        for item in order.items:
            manifest.append({
                "order_id": order.id,
                "order_date": order.order_date,
                "product_name": item.product.name,  # Automatic join lookup
                "quantity": item.quantity,
                "price_at_purchase": item.price_at_purchase
            })
            
    return manifest


def get_most_ordered_product(session: Session) -> tuple[str, int] | None:
    """
    Runs a high-performance aggregation query to find the single most ordered 
    product and the total number of units sold.

    SQL equivalent:
    SELECT products.name, SUM(order_items.quantity) AS total_ordered
    FROM order_items JOIN products ON products.id = order_items.product_id
    GROUP BY products.id ORDER BY total_ordered DESC LIMIT 1;

    :param session: Active SQLAlchemy database Session.
    :return: A tuple of (product_name, total_units_sold), or None if no orders exist.
    """
    # We query the Product's name, and the SUM of the order item quantities
    query = (
        select(Product.name, func.sum(OrderItem.quantity).label("total_ordered"))
        .join(OrderItem, Product.id == OrderItem.product_id)  # Join the tables
        .group_by(Product.id)  # Group results by product
        .order_by(func.sum(OrderItem.quantity).desc())  # Sort by highest sales
        .limit(1)  # Only return the top 1 result
    )
    
    # Execute the query
    result = session.execute(query).first()
    
    # Returns a tuple of (name, sum_quantity) if successful, otherwise None
    return tuple(result) if result else None


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