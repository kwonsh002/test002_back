from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
#import contextlib


# 연결할 db URL
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://kitri:rive123@db:3306/rive"
# SQLALCHEMY_DATABASE_URL = "sqlite:////./myapi.db"
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://rive:kitri123@rive-db.ctiemqwka664.ap-south-1.rds.amazonaws.com:3306/rive"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://admin:password123@rds-crider.czkkeoasq36g.ap-southeast-2.rds.amazonaws.com:3306/cirderdb"
# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://admin:password123@rds-crider.cheaiyuk4ex1.us-east-1.rds.amazonaws.com:3306/criderdb"
#SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:3778@localhost:3306/test002"
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://kwon001:Manoit123@test-test002-db.mysql.database.azure.com/test"


engine = create_engine(
    SQLALCHEMY_DATABASE_URL#, connect_args={"check_same_thread": False} 
    # 사용하려는 데이터베이스,SQLite일때 사용

) 


# 접속 끝나도 연결 상태 유지하기 위해 세션 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

#@contextlib.contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()