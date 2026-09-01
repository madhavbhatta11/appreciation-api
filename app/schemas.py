
from pydantic import BaseModel


class HomeResponse(BaseModel):

    message: str


class AppreciationResponse(BaseModel):

    message: str

    id: int


class AppreciationCountResponse(BaseModel):

    count: int


class AppreciationStatusResponse(BaseModel):

    appreciated: bool
