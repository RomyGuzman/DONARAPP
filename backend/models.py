from sqlalchemy import Column, Integer, String
from database import engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ConsultaDB(Base):
    __tablename__ = "consultas"

    id = Column(Integer, primary_key=True, index=True)
    texto = Column(String)
    resultado = Column(String)
    motivo = Column(String)

Base.metadata.create_all(bind=engine)