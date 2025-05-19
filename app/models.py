from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    STAFF = "staff"
    CUSTOMER = "customer"


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), default=UserRole.CUSTOMER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    customer = relationship("Customer", back_populates="user", uselist=False)
    reviews = relationship("Review", back_populates="user")


class Customer(Base):
    __tablename__ = "customer"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), unique=True, nullable=False)
    phone = Column(String(20))
    default_shipping_address_id = Column(Integer, ForeignKey("address.id"), nullable=True)
    default_billing_address_id = Column(Integer, ForeignKey("address.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="customer")
    addresses = relationship("Address", foreign_keys=[default_shipping_address_id])
    billing_addresses = relationship("Address", foreign_keys=[default_billing_address_id])
    orders = relationship("Order", back_populates="customer")
    reviews = relationship("Review", back_populates="customer")
    sales = relationship("Sale", back_populates="customer")


class Address(Base):
    __tablename__ = "address"
    id = Column(Integer, primary_key=True, index=True)
    street_address = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100))
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"


class Order(Base):
    __tablename__ = "order"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    shipping_address_id = Column(Integer, ForeignKey("address.id"), nullable=False)
    billing_address_id = Column(Integer, ForeignKey("address.id"), nullable=False)
    subtotal = Column(Float, nullable=False)
    shipping_cost = Column(Float, nullable=False)
    tax = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    tracking_number = Column(String(100))
    notes = Column(Text)

    # Relationships
    customer = relationship("Customer", back_populates="orders")
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])
    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    order_items = relationship("OrderItem", back_populates="order")
    payments = relationship("Payment", back_populates="order")
    sales = relationship("Sale", back_populates="order")

    # Indexes
    __table_args__ = (
        Index("idx_order_customer", "customer_id", "order_date"),
        Index("idx_order_status", "status", "order_date"),
    )


class OrderItem(Base):
    __tablename__ = "order_item"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_price = Column(Float, nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    __tablename__ = "payment"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    amount = Column(Float, nullable=False)
    payment_date = Column(DateTime(timezone=True), server_default=func.now())
    payment_method = Column(String(50), nullable=False)  # e.g., "credit_card", "paypal"
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    transaction_id = Column(String(100))
    
    # Relationships
    order = relationship("Order", back_populates="payments")

    # Indexes
    __table_args__ = (
        Index("idx_payment_order", "order_id", "payment_date"),
        Index("idx_payment_status", "status", "payment_date"),
    )


class Product(Base):
    __tablename__ = "product"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("category.id"))
    sku = Column(String(50))
    weight = Column(Float)
    dimensions = Column(String(50))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product")
    sales = relationship("Sale", back_populates="product")


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    products = relationship("Product", back_populates="category")


class Sale(Base):
    __tablename__ = "sale"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="sales")
    order = relationship("Order", back_populates="sales")
    customer = relationship("Customer", back_populates="sales")

    # Indexes
    __table_args__ = (
        Index("idx_sale_product", "product_id", "sale_date"),
        Index("idx_sale_customer", "customer_id", "sale_date"),
        Index("idx_sale_order", "order_id", "sale_date"),
    )


class Inventory(Base):
    __tablename__ = "inventory"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, nullable=False, default=10)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    product = relationship("Product", back_populates="inventory")
    history = relationship("InventoryHistory", back_populates="inventory")


class InventoryHistory(Base):
    __tablename__ = "inventory_history"
    id = Column(Integer, primary_key=True, index=True)
    inventory_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    quantity_change = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    reason = Column(String(255))  # e.g., "sale", "restock", "adjustment"

    # Relationships
    inventory = relationship("Inventory", back_populates="history")

    # Indexes
    __table_args__ = (
        Index("idx_inventory_history_inventory", "inventory_id", "timestamp"),
    )


class Review(Base):
    __tablename__ = "review"
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5 stars
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_verified_purchase = Column(Boolean, default=False)

    # Relationships
    product = relationship("Product", back_populates="reviews")
    customer = relationship("Customer", back_populates="reviews")
    user = relationship("User", back_populates="reviews")

    # Indexes
    __table_args__ = (
        Index("idx_review_product", "product_id", "created_at"),
        Index("idx_review_customer", "customer_id", "created_at"),
    )