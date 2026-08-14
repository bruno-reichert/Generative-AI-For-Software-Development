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
from sqlalchemy import create_engine, ForeignKey, String, Numeric, DateTime, func, select, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

# =====================================================================
# 1. Database Initialization
# =====================================================================
# Initialize the engine. In production, this URI would be loaded from an environment variable.
engine = create_engine("sqlite:///ecommerce.db", echo=False)

# In-memory cache stores
_PRODUCT_CACHE = {}


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
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Best Practice: Index foreign keys because they are frequently used in JOINs
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    
    order_date: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    
    # Best Practice: Index columns used in common filters (e.g., finding all 'shipped' orders)
    status: Mapped[str] = mapped_column(String(20), index=True, default="pending")

    # Relationships remain the same
    user: Mapped["User"] = relationship(back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    price_at_purchase: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Table-level arguments: Create a composite index on both order_id and product_id
    # This speeds up searches checking if a specific product is in a specific order.
    __table_args__ = (
        Index("ix_order_items_order_product", "order_id", "product_id"),
    )

    # Relationships remain the same
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

def get_product_by_id_cached(session: Session, product_id: int) -> Product | None:
    """
    Retrieves a product by its ID, utilizing a fast in-memory cache 
    to bypass database disk access.
    """
    # 1. Check if the product is already in our memory cache
    if product_id in _PRODUCT_CACHE:
        print(f"[CACHE HIT] Returning Product {product_id} from memory.")
        return _PRODUCT_CACHE[product_id]

    # 2. Cache Miss: Query the database
    print(f"[CACHE MISS] Fetching Product {product_id} from database file...")
    product = session.get(Product, product_id)
    
    if product:
        # Save the result in the cache for future queries
        _PRODUCT_CACHE[product_id] = product
        
    return product


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
    """Updates product stock and price, and invalidates the cache."""
    product = session.get(Product, product_id)
    if product:
        product.stock = new_stock
        product.price = Decimal(str(new_price))
        session.commit()
        
        # Cache Invalidation: Delete stale data from cache so it is fetched fresh next time
        if product_id in _PRODUCT_CACHE:
            del _PRODUCT_CACHE[product_id]
            print(f"[CACHE INVALIDATED] Cleared stale Product {product_id} from memory.")
            
    return product


def update_user_email(session: Session, user_id: int, new_email: str) -> User | None:
    """
    Updates the email address of an existing User.

    :param session: Active SQLAlchemy database Session.
    :param user_id: The primary key ID of the target User.
    :param new_email: The new email address string.
    :return: The updated User object if found, otherwise None.
    """
    user = session.get(User, user_id)
    if user:
        user.email = new_email
        session.commit()  # Dirty tracking automatically triggers SQL UPDATE here
    return user


def update_order_status(session: Session, order_id: int, new_status: str) -> Order | None:
    """
    Updates the status of an existing Order (e.g., from 'pending' to 'shipped').

    :param session: Active SQLAlchemy database Session.
    :param order_id: The primary key ID of the target Order.
    :param new_status: The new status string (e.g., 'shipped', 'completed', 'cancelled').
    :return: The updated Order object if found, otherwise None.
    """
    order = session.get(Order, order_id)
    if order:
        order.status = new_status
        session.commit()
    return order


def update_order_item_quantity(session: Session, order_item_id: int, new_quantity: int) -> OrderItem | None:
    """
    Updates the quantity of a specific item inside an order.

    :param session: Active SQLAlchemy database Session.
    :param order_item_id: The primary key ID of the target OrderItem.
    :param new_quantity: The new quantity integer (must be greater than 0).
    :return: The updated OrderItem object if found, otherwise None.
    :raises ValueError: If the new_quantity is 0 or negative.
    """
    # Defensive check: Prevent logically impossible quantities
    if new_quantity <= 0:
        raise ValueError("Database Integrity Error: Quantity must be a positive integer.")

    item = session.get(OrderItem, order_item_id)
    if item:
        item.quantity = new_quantity
        session.commit()
    return item

def modify_order_item(
    session: Session, 
    order_id: int, 
    product_id: int, 
    action: str, 
    quantity: int | None = None
) -> OrderItem | None:
    """
    Orchestrates high-level updates to an Order by adding, modifying, or 
    removing products inside that order.

    :param session: Active SQLAlchemy database Session.
    :param order_id: The primary key ID of the parent Order.
    :param product_id: The primary key ID of the Product to modify.
    :param action: The modification to perform: 'add', 'update', or 'remove'.
    :param quantity: The quantity integer (required for 'add' and 'update').
    :return: The affected OrderItem if added/updated, or None if removed.
    :raises KeyError: If the Order or Product does not exist.
    :raises ValueError: If the action is invalid or quantity is 0 or negative.
    """
    # 1. Validation: Verify the parent order exists
    order = session.get(Order, order_id)
    if not order:
        raise KeyError(f"Database Integrity Error: Order with ID {order_id} does not exist.")

    # 2. Query to see if this product is already in the order
    # (selects the OrderItem where order_id and product_id match)
    query = select(OrderItem).where(
        OrderItem.order_id == order_id, 
        OrderItem.product_id == product_id
    )
    existing_item = session.scalar(query)

    # =================================================================
    # CASE A: Adding a product
    # =================================================================
    if action == "add":
        if not quantity or quantity <= 0:
            raise ValueError("Invalid Quantity: Must specify a positive quantity to add.")
        
        if existing_item:
            # If the product already exists in the order, simply increase the quantity
            existing_item.quantity += quantity
            session.commit()
            return existing_item
        else:
            # If it's a new product, call our helper (which automatically captures price)
            return add_item_to_order(session, order_id, product_id, quantity)

    # =================================================================
    # CASE B: Updating quantity
    # =================================================================
    elif action == "update":
        if not quantity or quantity <= 0:
            raise ValueError("Invalid Quantity: Quantity must be a positive integer (cannot be 0 or negative).")
        
        if not existing_item:
            raise KeyError(f"Order Update Error: Product ID {product_id} is not in Order {order_id}.")
        
        existing_item.quantity = quantity
        session.commit()
        return existing_item

    # =================================================================
    # CASE C: Removing a product
    # =================================================================
    elif action == "remove":
        if not existing_item:
            raise KeyError(f"Order Update Error: Product ID {product_id} is not in Order {order_id}.")
        
        session.delete(existing_item)
        session.commit()
        return None

    else:
        raise ValueError(f"Invalid Action '{action}': Must be 'add', 'update', or 'remove'.")


# =====================================================================
# 7. CRUD: DELETE Operations
# =====================================================================
def delete_product(session: Session, product_id: int) -> bool:
    """Deletes a product, and invalidates the cache."""
    product = session.get(Product, product_id)
    if product:
        session.delete(product)
        session.commit()
        
        # Cache Invalidation
        if product_id in _PRODUCT_CACHE:
            del _PRODUCT_CACHE[product_id]
            print(f"[CACHE INVALIDATED] Removed deleted Product {product_id} from memory.")
        return True
    return False

def delete_user(session: Session, user_id: int) -> bool:
    """
    Deletes an existing User from the database.
    
    Warning: This triggers cascade deletions on all associated orders 
    and order items to preserve referential integrity.

    :param session: Active SQLAlchemy database Session.
    :param user_id: The primary key ID of the target User.
    :return: True if the deletion succeeded, False if the User was not found.
    """
    user = session.get(User, user_id)
    if user:
        session.delete(user)
        session.commit()
        return True
    return False


def delete_order(session: Session, order_id: int) -> bool:
    """
    Deletes an existing Order from the database.
    
    Warning: This triggers cascade deletions on all associated order items.

    :param session: Active SQLAlchemy database Session.
    :param order_id: The primary key ID of the target Order.
    :return: True if the deletion succeeded, False if the Order was not found.
    """
    order = session.get(Order, order_id)
    if order:
        session.delete(order)
        session.commit()
        return True
    return False


def delete_order_item(session: Session, order_item_id: int) -> bool:
    """
    Deletes a specific OrderItem from the database by its ID.

    :param session: Active SQLAlchemy database Session.
    :param order_item_id: The primary key ID of the target OrderItem.
    :return: True if the deletion succeeded, False if the OrderItem was not found.
    """
    item = session.get(OrderItem, order_item_id)
    if item:
        session.delete(item)
        session.commit()
        return True
    return False