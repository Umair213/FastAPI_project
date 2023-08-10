from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:umairzafar2406@localhost/fastapi"

# Thirdly, we create an engine which is responsible to connect sqlalchemy to postgres
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
# Creating Session to talk to DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Creating a Base class, all of the models that we define to actually create our tables in postgres, they are gonna be extending this base class
Base = declarative_base()

# This will basically create a session everytime we request we are gonna make a session and then after the request is done we are gonna close it.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
