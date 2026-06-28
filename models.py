from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Territory(Base):
    __tablename__ = "territories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    region = Column(String(100), nullable=False)
    country_group = Column(String(100), nullable=False)

    orders = relationship("SalesOrder", back_populates="territory_rel")

class Customer(Base):
    __tablename__ = "customers"
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    country = Column(String(100), nullable=False)
    city = Column(String(100), nullable=False)
    segment = Column(String(50), nullable=False)

    orders = relationship("SalesOrder", back_populates="customer")

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=False)
    list_price = Column(Numeric(10, 2), nullable=False)
    standard_cost = Column(Numeric(10, 2), nullable=False)

    order_items = relationship("SalesOrderItem", back_populates="product")

class SalesOrder(Base):
    __tablename__ = "sales_orders"
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    order_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    total_amount = Column(Numeric(15, 2), nullable=False)
    territory = Column(Integer, ForeignKey("territories.id"))

    customer = relationship("Customer", back_populates="orders")
    territory_rel = relationship("Territory", back_populates="orders")
    items = relationship("SalesOrderItem", back_populates="order")

class SalesOrderItem(Base):
    __tablename__ = "sales_order_items"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("sales_orders.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(15, 2), nullable=False)

    order = relationship("SalesOrder", back_populates="items")
    product = relationship("Product", back_populates="order_items")
