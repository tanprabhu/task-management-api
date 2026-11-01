from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Task, User
from app.schemas import (
    TaskCreate,
    TaskResponse,
    TaskUpdate,
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)

DatabaseSession = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]
TaskId = Annotated[int, Path(gt=0)]

@router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(
    task_data: TaskCreate,
    database: DatabaseSession,
    current_user: CurrentUser,
) -> Task:
    task = Task(
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        owner_id=current_user.id,
    )

    database.add(task)
    database.commit()
    database.refresh(task)

    return task


def get_owned_task(
    database: Session,
    user_id: int,
    task_id: int,
) -> Task:
    task = database.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.owner_id == user_id,
        )
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found.",
        )

    return task


@router.get(
    "",
    response_model=list[TaskResponse],
)
def list_tasks(
    database: DatabaseSession,
    current_user: CurrentUser,
) -> list[Task]:
    statement = (
        select(Task)
        .where(Task.owner_id == current_user.id)
        .order_by(Task.created_at.desc())
    )

    return list(database.scalars(statement).all())


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def get_task(
    task_id: TaskId,
    database: DatabaseSession,
    current_user: CurrentUser,
) -> Task:
    return get_owned_task(
        database=database,
        user_id=current_user.id,
        task_id=task_id,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def update_task(
    task_id: TaskId,
    task_data: TaskUpdate,
    database: DatabaseSession,
    current_user: CurrentUser,
) -> Task:
    task = get_owned_task(
        database=database,
        user_id=current_user.id,
        task_id=task_id,
    )

    updates = task_data.model_dump(
        exclude_unset=True,
    )

    for field_name, value in updates.items():
        setattr(task, field_name, value)

    database.commit()
    database.refresh(task)

    return task

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_task(
    task_id: TaskId,
    database: DatabaseSession,
    current_user: CurrentUser,
) -> Response:
    task = get_owned_task(
        database=database,
        user_id=current_user.id,
        task_id=task_id,
    )

    database.delete(task)
    database.commit()

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )