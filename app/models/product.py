from sqlalchemy import Column, Enum, Integer, String, ForeignKey, Float, DateTime, Text
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
    # should also be a list of metadata
    id = mapped_column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status= Column(Enum(ProductStatus),nullable=True,default=ProductStatus.published)
    image_url = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("ProductCategory", back_populates="products")
