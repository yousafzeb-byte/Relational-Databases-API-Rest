# E-commerce API

**Author:** Yousaf Zeb | **Date:** December 23, 2025

## Overview

RESTful API for an e-commerce system managing users, products, and orders with MySQL database.

**Tech Stack:** Flask, SQLAlchemy, Marshmallow, MySQL

**Features:**

- Full CRUD operations for Users, Products, Orders
- One-to-Many: User → Orders
- Many-to-Many: Orders ↔ Products
- Input validation & error handling
- Environment variables for security

## Quick Start

### 1. Setup Database

```sql
CREATE DATABASE ecommerce_api;
```

### 2. Install Dependencies

```bash
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and add your MySQL password:

```
DB_PASSWORD=your_password
```

### 4. Run Application

```bash
python ecommerce_api.py
```

API available at: `http://127.0.0.1:5000`

## API Endpoints

### Users

- `GET /users` - Get all users
- `GET /users/<id>` - Get user by ID
- `POST /users` - Create user
- `PUT /users/<id>` - Update user
- `DELETE /users/<id>` - Delete user

### Products

- `GET /products` - Get all products
- `GET /products/<id>` - Get product by ID
- `POST /products` - Create product
- `PUT /products/<id>` - Update product
- `DELETE /products/<id>` - Delete product

### Orders

- `POST /orders` - Create order
- `PUT /orders/<order_id>/add_product/<product_id>` - Add product to order
- `DELETE /orders/<order_id>/remove_product/<product_id>` - Remove product from order
- `GET /orders/user/<user_id>` - Get user's orders
- `GET /orders/<order_id>/products` - Get order's products

### Example Requests

**Create User:**

```json
POST /users
{
  "name": "John Doe",
  "address": "123 Main St",
  "email": "john@example.com"
}
```

**Create Product:**

```json
POST /products
{
  "product_name": "Laptop",
  "price": 999.99
}
```

**Create Order:**

```json
POST /orders
{
  "user_id": 1
}
```

## Testing

Import `Ecommerce_API.postman_collection.json` into Postman to test all endpoints.

**Test Flow:**

1. Create users and products
2. Create orders
3. Add products to orders
4. Query orders and products
5. Update and delete records

## Project Structure

```
Ecommerce-API-Final-Project/
├── ecommerce_api.py                      # Main application
├── requirements.txt                      # Dependencies
├── .env                                  # Environment variables (not in repo)
├── .env.example                          # Environment template
├── .gitignore                            # Git ignore rules
├── ECOMMERCE_API_README.md              # Documentation
└── Ecommerce_API.postman_collection.json # API tests
```

---

**Author:** Yousaf Zeb | Coding Temple 2025
