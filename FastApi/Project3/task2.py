from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

feedbacks = []

class Contact(BaseModel):
    email: str = Field(pattern=r"[^@]+@[^@]+\.[^@]+", description="Incorrect email")
    phone: str = Field(default=None, min_length=7, max_length=15, pattern=r"^[0-9]+$")


class Feedback(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="String should have at least 2 characters")
    message: str = Field(min_length=10, max_length=500, description="String should have at least 10 characters")
    contact: Contact


    @field_validator('message')
    def validate_msg(cls, value):
        t_value = value.lower()

        if 'редиск' in t_value or 'бяк' in t_value or 'козявк' in t_value:
            raise ValueError('Использование недопустимых слов')

        return value


    

app = FastAPI()


@app.post('/feedback')
async def feedback(feedback: Feedback, is_premium: bool = False):
    feedbacks.append(feedback.model_dump())

    ans = {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}

    if is_premium:
        ans['message'] =  ans['message'] + ' Ваш отзыв будет рассмотрен в приоритетном порядке.'

    return ans

"""
@app.post('/feedback')
async def feedback(feedback: Feedback):
    feed.append(feedback.model_dump())
    return {'message': f'Thank you, {feedback.name}.'}
"""

