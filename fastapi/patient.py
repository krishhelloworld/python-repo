from pydantic import (
    BaseModel,
    Field,
    field_validator,
    model_serializer,
    model_validator,
    ConfigDict,
    PrivateAttr,
    computed_field,
    SecretStr,
)
import hmac
from datetime import datetime, timezone
from typing import Any
from dump_database import DatabaseModel
from token_hashing import generate_token, hash_token
from address import Address
from gender import Gender


class Patient(DatabaseModel):
    model_config = ConfigDict(extra="forbid", validate_assignment=True)

    name: str = Field(..., min_length=5, max_length=40)
    gender: Gender = Field(description="Gender", examples=["male", "female"])
    address: Address
    age: int = Field(..., lt=100, gt=18)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), frozen=True
    )
    token_hash: SecretStr = Field(
        default_factory=lambda data: hash_token(data["token"]), frozen=True, repr=False
    )

    @model_validator(mode="after")
    def verify_token(self) -> "Patient":
        object.__setattr__(
            self,
            "verified_at",
            datetime.now(timezone.utc),
        )
        return self

    @field_validator("gender", mode="before")
    @classmethod
    def gender_validation(cls, value) -> Gender:
        gender = value.lower()
        return gender
