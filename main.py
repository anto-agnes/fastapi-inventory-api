from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# 1. Database Setup
DATABASE_URL = "sqlite:///./inventory.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 2. Database Model
class ItemModel(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    quantity = Column(Integer)

Base.metadata.create_all(bind=engine)

# 3. Pydantic Schemas (Validation)
class ItemCreate(BaseModel):
    name: str
    price: float
    quantity: int

class ItemResponse(ItemCreate):
    id: int
    class Config:
        from_attributes = True

# 4. FastAPI App Setup
app = FastAPI(title="Inventory Management API")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 5. API Endpoints
@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = ItemModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[ItemResponse])
def read_items(db: Session = Depends(get_db)):
    return db.query(ItemModel).all()

@app.get("/items/{item_id}", response_model=ItemResponse)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ItemModel).filter(ItemModel.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item