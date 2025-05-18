import uvicorn
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional

from starlette.requests import Request
from starlette.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# Список користувачів
users: List[dict] = [
    {"id": 1, "name": "Олена Іваненко", "email": "olena@example.com", "city": "Київ"},
    {"id": 2, "name": "Андрій Петренко", "email": "andriy@example.com", "city": "Львів"},
    {"id": 3, "name": "Марія Коваленко", "email": "maria@example.com", "city": "Одеса"},
]

@app.get("/")
def read_root(request: Request):
    # Дані, які будуть передані в шаблон
    data = {"message": "Hello, World!"}
    # Відображення сторінки з використанням Jinja2
    return templates.TemplateResponse("index.html", {"request": request, "data": data, "users": users})
# Лічильник для генерації унікальних ID
next_id = 1

# Модель для створення користувача
class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Ім'я користувача")
    email: str
    city: str = Field(..., min_length=2, description="Місто користувача")

# Модель для відповіді з ID
class User(UserCreate):
    id: int

# Створення нового користувача
@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    global next_id

    # Перевірка унікальності email
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Користувач з таким email вже існує")

    user_dict = user.model_dump()
    user_dict["id"] = next_id
    next_id += 1

    users.append(user_dict)
    return user_dict

# Отримання всіх користувачів або фільтр за містом
@app.get("/users/", response_model=List[User])
async def get_users(city: Optional[str] = Query(None, description="Фільтр за містом")):
    if city:
        filtered = [u for u in users if u["city"].lower() == city.lower()]
        if not filtered:
            raise HTTPException(status_code=404, detail="Користувачі не знайдені")
        return filtered
    return users

# Оновлення користувача за ID
@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: int, user_data: UserCreate):
    for u in users:
        if u["id"] == user_id:
            u.update(user_data.dict())
            return u
    raise HTTPException(status_code=404, detail="Користувача не знайдено")

# Видалення користувача за ID
@app.delete("/users/{user_id}")
async def delete_user(user_id: int):
    for u in users:
        if u["id"] == user_id:
            users.remove(u)
            return {"message": "Користувача видалено"}
    raise HTTPException(status_code=404, detail="Користувача не знайдено")


if __name__ == "__main__":
    uvicorn.run(app)