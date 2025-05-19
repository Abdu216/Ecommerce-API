# E-commerce Admin API

A powerful backend API built with FastAPI to power e-commerce admin dashboards, providing comprehensive insights into sales, revenue, and inventory management.

## Features

### Sales Analytics
- Detailed sales data retrieval and filtering
- Revenue analysis (daily/weekly/monthly/annual)
- Period comparison functionality
- Category-wise sales tracking

### Inventory Management
- Real-time inventory status
- Low stock alerts
- Inventory history tracking
- Stock level management

## Technical Stack

- **Framework**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT
- **Documentation**: Swagger UI (automatic via FastAPI)

## Project Structure

```
ecommerce_admin_api/
├── alembic/              # Database migrations
├── app/
│   ├── api/             # API endpoints
│   ├── core/            # Core configurations
│   ├── db/              # Database models and sessions
│   ├── schemas/         # Pydantic models
│   └── services/        # Business logic
├── scripts/
│   └── demo_data.py     # Script to populate demo data
├── tests/               # Test cases
├── .env                 # Environment variables
├── requirements.txt     # Project dependencies
└── README.md           # Project documentation
```

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd ecommerce_admin_api
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file in the root directory with:
   ```
   # Database settings
   MYSQL_USER=root
   MYSQL_PASSWORD=your_mysql_password
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_DATABASE=ecommerce_admin

   # Security settings
   SECRET_KEY=your_secret_key_here

   # CORS settings
   BACKEND_CORS_ORIGINS=["http://localhost:3000"]
   ```

5. **Initialize Database**
   First, create the database:
   ```sql
   CREATE DATABASE IF NOT EXISTS ecommerce_admin;
   ```

   Then run the migrations:
   ```bash
   alembic upgrade head
   ```

6. **Run the Application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

Once the server is running, access the API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Base API URL: `http://localhost:8000/api/v1`

### API Endpoints

#### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - User logout

#### Users
- `GET /api/v1/users/me` - Get current user profile
- `PUT /api/v1/users/me` - Update current user profile
- `GET /api/v1/users/{id}` - Get user by ID
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user
- `GET /api/v1/users/{id}/activity` - Get user activity history

#### Products
- `GET /api/v1/products/` - List all products with pagination and filters
- `POST /api/v1/products/` - Create a new product
- `GET /api/v1/products/{id}` - Get product details
- `PUT /api/v1/products/{id}` - Update product
- `DELETE /api/v1/products/{id}` - Delete product
- `GET /api/v1/products/{id}/reviews` - Get product reviews
- `POST /api/v1/products/{id}/reviews` - Add product review

#### Categories
- `GET /api/v1/categories/` - List all categories with optional parent filter
- `POST /api/v1/categories/` - Create a new category
- `GET /api/v1/categories/{id}` - Get category details with subcategories
- `PUT /api/v1/categories/{id}` - Update category
- `DELETE /api/v1/categories/{id}` - Delete category
- `GET /api/v1/categories/{id}/products` - Get products in category

#### Inventory
- `GET /api/v1/inventory/` - Get current inventory status with filters
- `GET /api/v1/inventory/alerts` - Get low stock alerts
- `PUT /api/v1/inventory/{id}` - Update inventory levels
- `GET /api/v1/inventory/history` - Get inventory history with date range
- `POST /api/v1/inventory/adjust` - Make inventory adjustment
- `GET /api/v1/inventory/reports` - Generate inventory reports

#### Sales & Analytics
- `GET /api/v1/sales/` - List all sales with filters
- `POST /api/v1/sales/` - Record a new sale
- `GET /api/v1/sales/{id}` - Get sale details
- `GET /api/v1/sales/analytics` - Get sales analytics with date range
- `GET /api/v1/sales/revenue` - Get revenue reports
- `GET /api/v1/sales/trends` - Get sales trends analysis
- `GET /api/v1/sales/forecasts` - Get sales forecasts

## Database Models

### User Model
```python
class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Product Model
```python
class Product(Base):
    __tablename__ = "products"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    price = Column(Numeric(10, 2), nullable=False)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    sku = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", uselist=False)
    reviews = relationship("Review", back_populates="product")
```

### Category Model
```python
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref=backref("parent", remote_side=[id]))
```

### Inventory Model
```python
class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), unique=True)
    quantity = Column(Integer, nullable=False, default=0)
    low_stock_threshold = Column(Integer, default=10)
    last_restock_date = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("Product", back_populates="inventory")
    history = relationship("InventoryHistory", back_populates="inventory")
```

### Sale Model
```python
class Sale(Base):
    __tablename__ = "sales"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    total_amount = Column(Numeric(10, 2), nullable=False)
    sale_date = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    product = relationship("Product")
```

### Review Model
```python
class Review(Base):
    __tablename__ = "reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    product = relationship("Product", back_populates="reviews")
    user = relationship("User")
```

## Error Handling

The API uses standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

## Security

- All sensitive data should be stored in the `.env` file
- Database passwords and API keys should never be committed to version control
- CORS is configured to allow specific origins only
- JWT authentication is implemented for protected endpoints

