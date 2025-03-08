from pydantic import BaseModel


class ChangeAutoconfirmSchema(BaseModel):
    autoconfirm: bool
