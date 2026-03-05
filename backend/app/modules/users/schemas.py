from pydantic import BaseModel


class UserBase(BaseModel):
    email: str


class UserOut(UserBase):
    id: int
    name_user: str
    role: str | None = None

    class Config:
        orm_mode = True
