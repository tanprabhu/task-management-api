from datetime import datetime

from typing import Annotated

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)

from app.models import TaskPriority, TaskStatus

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

TaskTitle = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
        max_length=200,
    ),
]


class TaskCreate(BaseModel):
    title: TaskTitle

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM


class TaskUpdate(BaseModel):
    title: TaskTitle | None = None

    description: str | None = Field(
        default=None,
        max_length=5000,
    )

    status: TaskStatus | None = None
    priority: TaskPriority | None = None

    @model_validator(mode="after")
    def validate_update(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided.")

        non_nullable_fields = {
            "title",
            "status",
            "priority",
        }

        for field_name in non_nullable_fields:
            if (
                field_name in self.model_fields_set
                and getattr(self, field_name) is None
            ):
                raise ValueError(
                    f"{field_name} cannot be null."
                )

        return self


class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority
    owner_id: int
    created_at: datetime
    updated_at: datetime