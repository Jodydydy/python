from typing import List
import uuid

from fastapi import Depends, FastAPI
from  sqlalchemy.orm import Session

from models import ProductCreate, Product, Base
from session import get_db, engine



app = FastAPI()


# Функция для добавления продуктов в базу данных
def add_products(products: List[ProductCreate], db: Session):
    for product_data in products:
        product = Product(
            id=uuid.uuid4(),
            title=product_data.title,
            price=product_data.price,
            count=product_data.count,
            # Первый запуск без поля description. Потом раскомментируем для добавления этого поля.
            # description=product_data.description
        )
        db.add(product)
    db.commit()


# Конечная точка для добавления продуктов через API
@app.post("/products/")
def create_products(products: List[ProductCreate], db: Session = Depends(get_db)):
    add_products(products, db)
    return {"message": "Products added successfully"}


# Создаем таблицы в базе данных, если они еще не существуют
Base.metadata.create_all(bind=engine)

# Добавляем код для запуска приложения через uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)