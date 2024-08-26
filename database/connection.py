from typing import Final
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus

db_user = "postgres"
db_password = "VrPost@Server"
db_host = "192.168.50.2"
db_port = "8745"
db_name = "si_dash"

encoded_password = quote_plus(db_password)

DATABASE_URL: Final[str] = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


