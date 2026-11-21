from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession


from database import get_session
from models import CustomExceptionModel, Product, ProductCreate, ProductFilter, ProductResponse, ProductPage


app = FastAPI()


class CustomExceptionA(HTTPException):
    def __init__(self, detail: str, status_code: int, message: str):
        super().__init__(status_code=400, detail=detail)
        self.message = message   


class CustomExceptionB(HTTPException):
    def __init__(self, detail: str, status_code: int, message: str):
        super().__init__(status_code=404, detail=detail)     
        self.message = message   


@app.exception_handler(CustomExceptionA)
async def custom_exception_a_handler(request: Request, exc: CustomExceptionA) -> JSONResponse:
    error = jsonable_encoder(CustomExceptionModel(status_code=exc.status_code, er_message=exc.message,
                                                  er_details=exc.detail))

    return JSONResponse(status_code=exc.status_code, content=error)


@app.exception_handler(CustomExceptionB)
async def custom_exception_b_handler(request: Request, exc: CustomExceptionB) -> JSONResponse:
    error = jsonable_encoder(CustomExceptionModel(status_code=exc.status_code, er_message=exc.message,
                                                  er_details=exc.detail))

    return JSONResponse(status_code=exc.status_code, content=error)


@app.post("/products", response_model=ProductResponse)
async def create_product(data: ProductCreate, session: AsyncSession = Depends(get_session)):

    product = Product(**data.model_dump())

    session.add(product)
    await session.commit()
    await session.refresh(product)

    return product


@app.get("/products",
          response_model=ProductPage,
          status_code=status.HTTP_200_OK,
          responses={
              status.HTTP_200_OK: {'model': ProductPage},
              status.HTTP_400_BAD_REQUEST: {'model': CustomExceptionModel},
              status.HTTP_404_NOT_FOUND: {'model': CustomExceptionModel},
          },)
async def get_products(filters: Annotated[ProductFilter, Query()],
                        session: AsyncSession = Depends(get_session)):


    stmt = select(Product)

    if filters.min_price is not None:
        stmt = stmt.where(Product.price >= filters.min_price)

    if filters.max_price is not None:
        stmt = stmt.where(Product.price <= filters.max_price)

    if filters.title is not None:
        stmt = stmt.where(Product.title.ilike(f"%{filters.title}%"))    
    else:
        raise CustomExceptionA(detail='No title', status_code=400, message="Parametr title was not set")                

    if filters.in_stock:
        stmt = stmt.where(Product.count > 0)


    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = await session.scalar(count_stmt)        

    sort_fields = {
        "id": Product.id,
        "title": Product.title,
        "price": Product.price,
        "count": Product.count
    }        

    sort_column = sort_fields[filters.sort_by]

    if filters.order == "desc":
        stmt = stmt.order_by(sort_column.desc(), Product.id.asc())
    else:
        stmt = stmt.order_by(sort_column.asc(), Product.id.asc())


    stmt = stmt.limit(filters.limit).offset(filters.offset)

    result = await session.scalars(stmt)
    products = result.all() 
    if not products:
        raise CustomExceptionB(detail='No products', status_code=404, message="No elements was founded")

    

    return ProductPage(
        items=products,
        total=total,
        limit=filters.limit,
        offset=filters.offset,
        has_next=filters.offset + len(products) < total
    )