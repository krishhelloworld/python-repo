from pydantic import BaseModel,model_serializer
from typing import Any

## this class override the pydantic serailization(mode =wrap) and add the private Attr(like, verified_at,etc)
class DatabaseModel(BaseModel):
    @model_serializer(mode="wrap")
    def serialize(self, handler: Any) -> dict:
        # Calling handler(self) inside the serializer-> produces a dictionary(self->public attr) then we can add all the remainaing attr
        data = handler(self)

        for name in self.__private_attributes__:
            value = getattr(self, name, None)
            if value is not None:
                data[name.lstrip("_")] = value

        return data
