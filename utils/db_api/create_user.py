from sqlalchemy.orm import  DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy import String, create_engine,Column,Integer, BigInteger
from datetime import datetime
from sqlalchemy import Column, String, BigInteger, DateTime
from sqlalchemy.ext.declarative import declarative_base
class Base(DeclarativeBase):
    pass

class User(Base):
  __tablename__ = "user"

  # ID ustuni
  id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
  hisob: Mapped[int] = mapped_column(String(255), nullable=True,default=0)
  username: Mapped[str] = mapped_column(String(115), nullable=True)
  name: Mapped[str] = mapped_column(String(255), nullable=False)


class Transaction(Base):
  __tablename__ = 'transactions'

  order_id = Column(String, primary_key=True,unique=True,nullable=False, index=True)
  telegram_id = Column(BigInteger, nullable=False)
  summa = Column(BigInteger, nullable=False)
  holat = Column(String, default="pending")
  vaqti = Column(DateTime, default=datetime.now)


class Numbers_list(Base):
  __tablename__ = 'number_list'
  id = Column(Integer, primary_key=True, )
  country = Column(String,nullable=False)
  price = Column(BigInteger,nullable=False)

class Order_numbers(Base):
  __tablename__ = 'orders_number'
  id = Column(Integer, primary_key=True, )
  country = Column(String, nullable=False)
  owner_number = Column(BigInteger,nullable=False)
  number = Column(String)
  status = Column(String,default="WAITING")
  kod = Column(BigInteger,default='00000')
  pas2 = Column(String,default='None')



engine = create_engine("sqlite:///database.db")


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

