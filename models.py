from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy.sql import func

DATABASE_URI = 'sqlite:///multi-level-marketing.db'
engine = create_engine(DATABASE_URI, echo=False)
Base = declarative_base()

Session = sessionmaker(bind=engine)


class Distributors(Base):
    __tablename__ = 'distributors'

    id = Column(Integer, primary_key=True, index=True)
    distributor_name = Column(String(50), unique=True, index=True, nullable=False)
    added_by_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    sales = relationship('Sales', back_populates='distributor', cascade='all, delete-orphan')
    commissions = relationship('Commissions', back_populates='distributor', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Distributor(id={self.id}, name={self.distributor_name}, created_at={self.created_at})>"


class Products(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(50), unique=True, index=True, nullable=False)
    product_price = Column(Numeric(10, 2), nullable=False)  # Use Numeric for precise money storage
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    sales = relationship('Sales', back_populates='product')

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.product_name}, price={self.product_price})>"


class Sales(Base):
    __tablename__ = 'sales'

    id = Column(Integer, primary_key=True, index=True)
    distributor_id = Column(Integer, ForeignKey('distributors.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    product_price = Column(Numeric(10, 2), nullable=False)  # Use Numeric for product price
    earned = Column(Numeric(10, 2), nullable=False)  # Use Numeric for earned commissions
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    distributor = relationship('Distributors', back_populates='sales')
    product = relationship('Products', back_populates='sales')
    commissions = relationship('Commissions', back_populates='sale', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Sale(id={self.id}, earned={self.earned}, product_price={self.product_price})>"


class Commissions(Base):
    __tablename__ = 'commissions'

    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=False)
    distributor_id = Column(Integer, ForeignKey('distributors.id'), nullable=False)
    commission = Column(Numeric(10, 2), nullable=False)  # Use Numeric for commission

    # Relationships
    sale = relationship('Sales', back_populates='commissions')
    distributor = relationship('Distributors', back_populates='commissions')

    def __repr__(self):
        return f"<Commissions(id={self.id}, distributor_id={self.distributor_id}, sale_id={self.sale_id}, commission={self.commission})>"


def init_db():
    """Create all tables in the database."""
    Base.metadata.create_all(bind=engine)
