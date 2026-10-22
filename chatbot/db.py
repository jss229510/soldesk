import os
from pathlib import Path

import oracledb
from dotenv import load_dotenv

# 같은 폴더의 .env 를 읽는다 (이미 있는 환경변수는 덮어쓰지 않음)
load_dotenv(Path(__file__).with_name(".env"))


def get_connection():
    """Oracle 연결. Spring 과 같은 DB_URL/DB_USERNAME/DB_PASSWORD 환경변수를 쓴다"""
    dsn = (os.getenv("DB_DSN")
           or os.getenv("DB_URL", "").replace("jdbc:oracle:thin:@", "")
           or "localhost:1521/XEPDB1")
    user = os.getenv("DB_USERNAME")
    password = os.getenv("DB_PASSWORD")
    if not user or not password:
        raise ValueError("DB_USERNAME 또는 DB_PASSWORD 환경변수가 없습니다.")
    return oracledb.connect(user=user, password=password, dsn=dsn)
