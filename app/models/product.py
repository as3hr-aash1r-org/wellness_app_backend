from sqlalchemy import Column, Enum, Integer, String, ForeignKey, Float, DateTime, Text, Boolean
from sqlalchemy.orm import relationship, mapped_column
from sqlalchemy.sql import func
from app.database.base import Base
import enum

class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False, unique=True)
    created_at = mapped_column(DateTime(timezone=True), server_default=func.now())

    products = relationship("Product", back_populates="category", cascade="all, delete")


class ProductStatus(enum.Enum):
    published = "published"
    out_of_stock = "out of stock"
    low_stock = "low stock"    

class Product(Base):
    __tablename__ = "products"
    
    id = mapped_column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    sku = Column(String, nullable=True, unique=True)  # Stock Keeping Unit
    company = Column(String, nullable=True)
    product_group = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ProductStatus), nullable=True, default=ProductStatus.published)
    
    # Images
    image_url = Column(String, nullable=True)  # Main product image
    thumbnail_url = Column(String, nullable=True)  # Product thumbnail
    
    # Basic Info
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=False)
    tags = Column(Text, nullable=True)  # Comma-separated tags
    quantity = Column(Integer, nullable=True, default=0)
    best_seller = Column(Boolean, nullable=True, default=False)
    
    # Dimensions (in cm)
    length = Column(Float, nullable=True)
    width = Column(Float, nullable=True)
    height = Column(Float, nullable=True)
    
    # Weight & Volume
    net_weight = Column(Float, nullable=True)  # in grams
    gross_weight = Column(Float, nullable=True)  # in grams
    volume = Column(Float, nullable=True)  # in ml or cubic cm
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    category = relationship("ProductCategory", back_populates="products")
