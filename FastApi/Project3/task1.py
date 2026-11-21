from fastapi import FastAPI
from pydantic import BaseModel, Field, field_validator

feedbacks = []

class Feedback(BaseModel):
    name: str = Field(min_length=2, max_length=50, description="String should have at least 2 characters")
    message: str = Field(min_length=10, max_length=500, description="String should have at least 10 characters")


    @field_validator('message')
    def validate_msg(cls, value):
        t_value = value.lower()

        if 'редиск' in t_value or 'бяк' in t_value or 'козявк' in t_value:
            raise ValueError('Использование недопустимых слов')

        return value


    

app = FastAPI()


@app.post('/feedback')
async def feedback(feedback: Feedback):
    feedbacks.append(feedback.model_dump())

    return {"message": f"Спасибо, {feedback.name}! Ваш отзыв сохранён."}

"""
@app.post('/feedback')
async def feedback(feedback: Feedback):
    feed.append(feedback.model_dump())
    return {'message': f'Thank you, {feedback.name}.'}
"""

