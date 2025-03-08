from pydantic import BaseModel


class ChangeSubscriptionSchema(BaseModel):
    is_subscribed_to_email: bool
