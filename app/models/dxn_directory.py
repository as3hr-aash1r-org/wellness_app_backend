from sqlalchemy import Column, Integer, String
from app.database.base import Base

class DXNDirectory(Base):
    __tablename__ = "dxn_directory"

    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, nullable=False)
    person = Column(String, nullable=False)
    position = Column(String, nullable=True)
    phone1 = Column(String, nullable=True)
    phone2 = Column(String, nullable=True)
    whatsapp1 = Column(String, nullable=True)
    whatsapp2 = Column(String, nullable=True)
    email1 = Column(String, nullable=True)
    email2 = Column(String, nullable=True)
    website = Column(String, nullable=True)
    address_line1 = Column(String, nullable=True)
    address_line2 = Column(String, nullable=True)
    city = Column(String, nullable=True)
    province_state = Column(String, nullable=True)
    price_list = Column(String, nullable=True)  # link
