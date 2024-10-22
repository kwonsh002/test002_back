from datetime import timedelta, datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from starlette import status


from database import get_db
from domain.users import users_crud, users_schema
import hashlib


ACCESS_TOKEN_EXPIRE_MINUTES = 60 *24
SECRET_KEY = "4ab2fce7a6bd79e1c014396315ed322dd6edb1c5d975c6b74a2904135172c03c"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


router = APIRouter(
    prefix="/api/users",
)

# 사용자 위치 확인 함수
# def get_user_location(ip: str) -> str:
#     try:
#         response = requests.get(f"https://ipinfo.io/{ip}/json")
#         response.raise_for_status()  # 요청이 실패한 경우 예외 발생
#         data = response.json()
#         return data.get("country", "Unknown")  # 기본값 설정
#     except requests.RequestException:
#         return "Unknown"  # 요청 실패 시 기본값
def get_user_location(request: Request) -> str:
    # CloudFront에서 전달된 국가 코드 가져오기
    country_code = request.headers.get("CloudFront-Viewer-Country")
    
    if country_code:
        return country_code  # 헤더에서 가져온 국가 코드 반환

# 사용자 생성 함수
@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def user_create(
    _user_create: users_schema.UserCreate,
    request: Request,
    db: Session = Depends(get_db)
):  
    print(f"Client Host: {request.client.host}")  # 추가 로그
    user = users_crud.get_existing_user(db, user_create=_user_create)
    
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='이미 존재하는 사용자입니다.')

    # 클라이언트의 IP 주소를 가져와 사용자 위치 확인
    user_country = get_user_location(request)
    
    print(f"User Country Code: {user_country}")  # 로그 추가
    
    # 빈값일 경우 "KR"로 할당
    if not user_country:
        user_country = "KR"
    
    # 한국 사용자만 회원가입 가능
    if user_country.upper() != "KR":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail='한국 사용자만 회원가입이 가능합니다.')

    user2 = users_crud.create_user(db=db, user_create=_user_create)
    
    if len(user2.user_pw) <= 1:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail='잘못된 비밀번호 설정입니다.')
    print(f"User Country Code2: {user_country}")  # 로그 추가
    users_crud.add_user(db, user2)



#login
@router.post("/login")
def user_login(_user_login: users_schema.Users,
               db: Session = Depends(get_db)):
    user = users_crud.get_user(db = db, username=_user_login.username)
    if user:
        return True
    else:
        return False
    


#token login
@router.post("/login/token", response_model=users_schema.Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                           db: Session = Depends(get_db)):   
    #check user and passwd
    user = users_crud.get_user(db, form_data.username)
    h_pw = users_crud.hash_pw(form_data.password)
    if not user or not (h_pw == user.user_pw):  #error 패스워드 비교 내용 수정 필요!!!!!!!!!!!!!
    #if not user or not hashlib.verify(form_data.user_pw, user.user_pw):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password ",
            headers={"WWW-Authenticate": "Bearer"},
        ) 
    #make access token
    data = {
        "sub": user.username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }
    access_token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "user_id": user.user_id
    }

"""
#get user 글쓰려면 로그인 해야함
#헤더 정보 토큰값으로 사용자 정보 조회
def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #jwt.decode() : 토큰을 복호화하여 토큰에 담겨있는 사용자명 get
        username: str = token_data.get("sub")
        if username is None:
            raise credentials_exception #사용자명이 없을 경우 예외 발생
    except JWTError:
        raise credentials_exception
    else:
        user = users_crud.get_user(db, username=username)
        if user is None:
            raise credentials_exception
        return user
"""
