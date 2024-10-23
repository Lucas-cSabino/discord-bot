import os

from typing import Final
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

#### Módulo responsável pela conexão com o banco de dados

load_dotenv()
DB_USER: Final[str] = os.getenv("DB_USER")
DB_PASSWORD: Final[str] = quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST: Final[str] = os.getenv("DB_HOST")
DB_PORT: Final[str] = os.getenv("DB_PORT")
DB_NAME: Final[str] = os.getenv("DB_NAME")

DATABASE_URL: Final[str] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
