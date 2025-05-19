import sys
import os
from datetime import datetime, timedelta
import random
from decimal import Decimal

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.session import engine, SessionLocal
from app.db.base_class import Base
from app.models import (
    User, Customer, Address, Category, Product, 
    Inventory, Order, OrderItem, Payment, Sale,
    UserRole, OrderStatus, PaymentStatus, InventoryHistory
)
from app.core.security import get_password_hash

# Sample data
users_data = [
    {
        "email": "admin@example.com",
        "hashed_password": get_password_hash("admin"),
        "full_name": "Admin User",
        "role": UserRole.ADMIN,
        "is_active": True
    },
    {
        "email": "staff@example.com",
        "hashed_password": get_password_hash("staff"),
        "full_name": "Staff User",
        "role": UserRole.STAFF,
        "is_active": True
    },
]

customer_users_data = [
    {
        "email": f"customer{i}@example.com",
        "hashed_password": get_password_hash(f"customer{i}"),
        "full_name": f"Customer {i}",
        "role": UserRole.CUSTOMER,
        "is_active": True
    }
    for i in range(1, 6)  # Create 5 customers
]

categories = [
    {"name": "Electronics", "description": "Electronic devices and accessories"},
    {"name": "Clothing", "description": "Apparel and fashion items"},
    {"name": "Home & Kitchen", "description": "Home appliances and kitchenware"},
    {"name": "Books", "description": "Books and educational materials"},
]

products_by_category = {
    "Electronics": [
        {
            "name": "Smartphone X",
            "description": "Latest smartphone with advanced features",
            "price": 999.99,
            "sku": "PHONE-X-001",
            "weight": 0.18,
            "dimensions": "15x7.5x0.8",
            "is_active": True
        },
        {
            "name": "Laptop Pro",
            "description": "High-performance laptop",
            "price": 1499.99,
            "sku": "LAP-PRO-001",
            "weight": 2.1,
            "dimensions": "35x24x1.8",
            "is_active": True
        },
        {
            "name": "Wireless Earbuds",
            "description": "Premium wireless earbuds",
            "price": 199.99,
            "sku": "EAR-BUD-001",
            "weight": 0.05,
            "dimensions": "5x5x2.5",
            "is_active": True
        }
    ],
    "Clothing": [
        {
            "name": "Classic T-Shirt",
            "description": "Cotton t-shirt",
            "price": 29.99,
            "sku": "SHIRT-CLS-001",
            "weight": 0.2,
            "dimensions": "30x20x2",
            "is_active": True
        },
        {
            "name": "Denim Jeans",
            "description": "Comfortable jeans",
            "price": 79.99,
            "sku": "JEAN-DNM-001",
            "weight": 0.6,
            "dimensions": "40x30x3",
            "is_active": True
        },
        {
            "name": "Winter Jacket",
            "description": "Warm winter jacket",
            "price": 149.99,
            "sku": "JACK-WIN-001",
            "weight": 1.2,
            "dimensions": "60x40x5",
            "is_active": True
        }
    ],
    "Home & Kitchen": [
        {
            "name": "Coffee Maker",
            "description": "Automatic coffee maker",
            "price": 89.99,
            "sku": "COFFEE-MKR-001",
            "weight": 3.5,
            "dimensions": "25x20x35",
            "is_active": True
        },
        {
            "name": "Blender",
            "description": "High-speed blender",
            "price": 69.99,
            "sku": "BLEND-001",
            "weight": 2.8,
            "dimensions": "20x20x40",
            "is_active": True
        },
        {
            "name": "Toaster",
            "description": "4-slice toaster",
            "price": 49.99,
            "sku": "TOAST-4S-001",
            "weight": 2.2,
            "dimensions": "30x20x20",
            "is_active": True
        }
    ],
    "Books": [
        {
            "name": "Python Programming",
            "description": "Learn Python programming",
            "price": 39.99,
            "sku": "BOOK-PY-001",
            "weight": 0.8,
            "dimensions": "25x20x2.5",
            "is_active": True
        },
        {
            "name": "Data Science Basics",
            "description": "Introduction to data science",
            "price": 44.99,
            "sku": "BOOK-DS-001",
            "weight": 0.9,
            "dimensions": "25x20x3",
            "is_active": True
        },
        {
            "name": "Web Development Guide",
            "description": "Complete web development guide",
            "price": 49.99,
            "sku": "BOOK-WEB-001",
            "weight": 1.1,
            "dimensions": "25x20x3.5",
            "is_active": True
        }
    ]
}

def clear_existing_data():
    db = SessionLocal()
    try:
        # Delete data in reverse order of dependencies
        db.query(Sale).delete()
        db.query(InventoryHistory).delete()
        db.query(Payment).delete()
        db.query(OrderItem).delete()
        db.query(Order).delete()
        db.query(Inventory).delete()
        db.query(Product).delete()
        db.query(Category).delete()
        db.query(Customer).delete()
        db.query(Address).delete()
        db.query(User).delete()
        db.commit()
        print("Existing data cleared successfully!")
    except Exception as e:
        print(f"Error clearing data: {e}")
        db.rollback()
    finally:
        db.close()

def create_demo_data():
    Base.metadata.create_all(bind=engine)
    clear_existing_data()  # Clear existing data before creating new data
    db = SessionLocal()
    
    try:
        # Create admin and staff users
        for user_data in users_data:
            user = User(**user_data)
            db.add(user)
        db.commit()

        # Create customer users and their profiles
        customers = []
        for user_data in customer_users_data:
            # Create user
            user = User(**user_data)
            db.add(user)
            db.flush()
            
            # Create customer profile
            customer = Customer(
                user_id=user.id,
                phone=f"+1555{random.randint(1000000, 9999999)}"
            )
            db.add(customer)
            customers.append(customer)
        db.commit()

        # Create addresses for customers
        for customer in customers:
            # Create shipping address
            shipping_address = Address(
                street_address=f"{random.randint(100, 999)} Main St",
                city="Sample City",
                state="Sample State",
                postal_code=str(random.randint(10000, 99999)),
                country="United States",
                is_default=True
            )
            db.add(shipping_address)
            db.flush()
            
            # Create billing address
            billing_address = Address(
                street_address=f"{random.randint(100, 999)} Billing St",
                city="Sample City",
                state="Sample State",
                postal_code=str(random.randint(10000, 99999)),
                country="United States",
                is_default=True
            )
            db.add(billing_address)
            db.flush()
            
            # Update customer with default addresses
            customer.default_shipping_address_id = shipping_address.id
            customer.default_billing_address_id = billing_address.id
        db.commit()
        
        # Create categories and store their IDs
        category_ids = {}
        for cat_data in categories:
            category = Category(**cat_data)
            db.add(category)
            db.flush()
            category_ids[category.name] = category.id
        db.commit()
        
        # Create products using category IDs
        db_products = []
        for category_name, products in products_by_category.items():
            category_id = category_ids[category_name]
            for prod_data in products:
                product = Product(**prod_data, category_id=category_id)
                db.add(product)
                db_products.append(product)
        db.commit()
        
        # Create inventory records
        for product in db_products:
            initial_quantity = random.randint(50, 200)
            inventory = Inventory(
                product_id=product.id,
                quantity=initial_quantity,
                low_stock_threshold=10
            )
            db.add(inventory)
            db.flush()
            
            # Add initial stock history
            history = InventoryHistory(
                inventory_id=inventory.id,
                quantity_change=initial_quantity,
                reason="initial stock"
            )
            db.add(history)
        db.commit()
        
        # Create orders and sales records (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        payment_methods = ["CREDIT_CARD", "DEBIT_CARD", "PAYPAL", "BANK_TRANSFER"]
        
        for _ in range(50):  # Create 50 random orders
            customer = random.choice(customers)
            order_date = start_date + timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # Randomly choose order status with weighted probability
            status_weights = [
                (OrderStatus.DELIVERED, 0.6),  # 60% delivered
                (OrderStatus.PENDING, 0.2),    # 20% pending
                (OrderStatus.PROCESSING, 0.1), # 10% processing
                (OrderStatus.CANCELLED, 0.1)   # 10% cancelled
            ]
            order_status = random.choices(
                [s[0] for s in status_weights],
                weights=[s[1] for s in status_weights]
            )[0]
            
            # Create order
            order = Order(
                customer_id=customer.id,
                order_date=order_date,
                status=order_status,
                shipping_address_id=customer.default_shipping_address_id,
                billing_address_id=customer.default_billing_address_id,
                subtotal=0,
                shipping_cost=10.00,
                tax=0,
                total=0,
                tracking_number=f"TRACK{random.randint(100000, 999999)}" if order_status != OrderStatus.CANCELLED else None,
                notes="Demo order"
            )
            db.add(order)
            db.flush()
            
            # Add 1-3 items to order
            subtotal = Decimal('0')
            for _ in range(random.randint(1, 3)):
                product = random.choice(db_products)
                quantity = random.randint(1, 3)
                unit_price = Decimal(str(product.price))
                item_total = unit_price * quantity
                subtotal += item_total
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=float(unit_price),
                    total_price=float(item_total)
                )
                db.add(order_item)
                
                # Update inventory and create history for delivered or processing orders
                if order_status in [OrderStatus.DELIVERED, OrderStatus.PROCESSING]:
                    inventory = db.query(Inventory).filter(
                        Inventory.product_id == product.id
                    ).first()
                    if inventory:
                        inventory.quantity -= quantity
                        
                        # Add inventory history
                        history = InventoryHistory(
                            inventory_id=inventory.id,
                            quantity_change=-quantity,
                            reason=f"order #{order.id}"
                        )
                        db.add(history)
                        
                        # Create sale record for delivered orders
                        if order_status == OrderStatus.DELIVERED:
                            sale = Sale(
                                product_id=product.id,
                                order_id=order.id,
                                customer_id=customer.id,
                                quantity=quantity,
                                unit_price=float(unit_price),
                                total_amount=float(item_total),
                                sale_date=order_date
                            )
                            db.add(sale)
            
            # Update order totals
            tax = subtotal * Decimal('0.1')  # 10% tax
            shipping_cost = Decimal('10.00')
            total = subtotal + tax + shipping_cost
            
            order.subtotal = float(subtotal)
            order.tax = float(tax)
            order.total = float(total)
            
            # Create payment record
            if order_status != OrderStatus.CANCELLED:
                payment_status = PaymentStatus.COMPLETED if order_status == OrderStatus.DELIVERED else PaymentStatus.PENDING
                payment = Payment(
                    order_id=order.id,
                    amount=float(total),
                    status=payment_status,
                    payment_date=order_date if payment_status == PaymentStatus.COMPLETED else None,
                    payment_method=random.choice(payment_methods),
                    transaction_id=f"TXN{random.randint(100000, 999999)}" if payment_status == PaymentStatus.COMPLETED else None
                )
                db.add(payment)
        
        db.commit()
        print("Demo data created successfully!")
        
    except Exception as e:
        print(f"Error creating demo data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    create_demo_data() 