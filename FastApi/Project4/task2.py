from fastapi import FastAPI
from pydantic import BaseModel
from typing import List

class Product(BaseModel):
    product_id: int
    name: str
    category: str
    price: float



sample_product_1 = {
    "product_id": 123,
    "name": "Smartphone",
    "category": "Electronics",
    "price": 599.99
}

sample_product_2 = {
    "product_id": 456,
    "name": "Phone Case",
    "category": "Accessories",
    "price": 19.99
}

sample_product_3 = {
    "product_id": 789,
    "name": "Iphone",
    "category": "Electronics",
    "price": 1299.99
}

sample_product_4 = {
    "product_id": 101,
    "name": "Headphones",
    "category": "Accessories",
    "price": 99.99
}

sample_product_5 = {
    "product_id": 202,
    "name": "Smartwatch",
    "category": "Electronics",
    "price": 299.99
}

sample_products = [Product(**sample_product_1), Product(**sample_product_2),
                    Product(**sample_product_3), Product(**sample_product_4), 
                    Product(**sample_product_5)]


app = FastAPI()


@app.get('/product/{product_id}', response_model=Product)
async def get_product(product_id: int):
    res = None

    for product in sample_products:
        if product.product_id == product_id:
            res = product

    return res            

@app.get('/products/search', response_model=List)
async def search_products(keyword: str, category: str = None, limit: int = 10):

    res = list()

    for product in sample_products:
        if keyword.lower() in product.name.lower():
            if category is not None:
                if product.category.lower() == category.lower():
                    res.append(product)
            else:
                res.append(product)    


    return res[:limit]            
