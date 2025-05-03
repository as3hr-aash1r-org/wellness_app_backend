from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.sql import func
from app.db import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False, unique=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="category", cascade="all, delete")


class Product(Base):
    __tablename__ = "products"
    # should also be a list of metadata
    id = mapped_columnn(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("ProductCategory", back_populates="products")
