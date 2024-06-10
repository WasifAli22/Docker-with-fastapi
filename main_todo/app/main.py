# main.py
from contextlib import asynccontextmanager
from typing import Union, Optional, Annotated
from app.settings import DATABASE_URL
from sqlmodel import Field, Session, SQLModel, create_engine, select, delete
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.model import Todo, TodoCreate, TodoUpdate


# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL
connection_string = str(DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)


# recycle connections after 5 minutes
# to correspond with the compute scale down
engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300,
    # echo=True
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# The first part of the function, before the yield, will
# be executed before the application starts.
# https://fastapi.tiangolo.com/advanced/events/#lifespan-function
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating tables..")
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan, title="Hello World API with DB", 
    version="0.0.1",
    servers=[
        {
            "url": "http://localhost:8000/", # ADD NGROK URL Here Before Creating GPT Action
            "description": "Development Server"
        }
        ])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/todos/", response_model=Todo)
def create_todo(todo: TodoCreate, session: Annotated[Session, Depends(get_session)]):
        add_todo = Todo.from_orm(todo)
        session.add(add_todo)
        session.commit()
        session.refresh(add_todo)
        return add_todo


@app.get("/todos/", response_model=list[Todo])
def read_todos(session: Annotated[Session, Depends(get_session)]):
        todos = session.exec(select(Todo)).all()
        return todos

# get single todo
@app.get("/todos/{todo_id}", response_model=Todo)
def read_single_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    todo = session.get(Todo, todo_id)
    return todo

@app.put("/todos/{todo_id}", response_model=Todo)
def update_single_todo(
    todo_id: int, todo: TodoUpdate, session: Annotated[Session, Depends(get_session)]
):
    db_todo = session.get(Todo, todo_id)

    if db_todo is None:
        return "Todo not found"

    todo_data = todo.dict(exclude_unset=True)

    for key, value in todo_data.items():
        # implement the logic that values should not be None and value="string"
        if value is not None and value != "string":
            setattr(db_todo, key, value)
            

    session.commit()
    session.refresh(db_todo)
    return db_todo

# delete todo
@app.delete("/todos/{todo_id}")
def delete_single_todo(todo_id: int, session: Annotated[Session, Depends(get_session)]):
    todo = session.get(Todo, todo_id)
    if todo is None:
        return "Todo not found"
    session.delete(todo)
    session.commit()
    return {"message": "Todo deleted successfully"}

# delete all todos
@app.delete("/todos/")
def delete_all_todos(session: Annotated[Session, Depends(get_session)]):
    session.exec(delete(Todo))
    session.commit()
    return {"message": "All todos deleted successfully"}