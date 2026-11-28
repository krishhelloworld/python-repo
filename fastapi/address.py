from pydantic import BaseModel,ConfigDict

class Address(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    city: str
    state: str
    pincode: str
