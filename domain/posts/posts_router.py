from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from starlette import status

from database import get_db
from domain.posts import posts_schema, posts_crud
#from domain.users.users_router import get_current_user
from models import Users
from sqlalchemy.exc import SQLAlchemyError
#post router 생성
router = APIRouter(
    prefix="/api/posts",
)


#post router를 FastAPI에 등록. .get() 요청되면 prefix 등록된 posts_list 실행
@router.get("/list")
def posts_list(db: Session = Depends(get_db), page: int = 0, size: int = 10):
    total, _posts_list = posts_crud.get_posts_list(db, skip=page*size, limit=size)
    return {'total': total, 'posts_list': _posts_list}


@router.get("/list/{post_id}", response_model = posts_schema.Posts)
def posts_detail(post_id: int, db: Session = Depends(get_db)):
    posts = posts_crud.get_post(db, post_id=post_id)
    return posts

# @router.post("/create", status_code = status.HTTP_204_NO_CONTENT)
# def post_create(_post_create: posts_schema.Posts,
#                 db: Session = Depends(get_db)):
#                 #current_user: Users = Depends(get_current_user)):
#     posts_crud.create_post(db = db, post_create=_post_create)#, user=current_user)



@router.post("/create", status_code=status.HTTP_204_NO_CONTENT)
def post_create(_post_create: posts_schema.Posts,
                db: Session = Depends(get_db)):
    try:
        # 데이터베이스에 새 포스트를 생성합니다.
        posts_crud.create_post(db=db, post_create=_post_create)
    except SQLAlchemyError as e:
        # SQLAlchemy 관련 예외 처리
        db.rollback()  # 데이터베이스 세션을 롤백합니다.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="데이터베이스 오류가 발생했습니다."
        ) from e
    except ValueError as e:
        # 데이터 유효성 검사 관련 예외 처리
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="잘못된 데이터가 전송되었습니다."
        ) from e
    except Exception as e:
        # 그 외 모든 예외 처리
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="서버에서 알 수 없는 오류가 발생했습니다."
        ) from e
"""
@router.put("/update", status_code=status.HTTP_204_NO_CONTENT)
def post_update(_post_update: posts_schema.PostUpdate, db: Session = Depends(get_db)):
    db_post = posts_crud.get_post(db, post_id=_post_update.post_id)
    if not db_post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="데이터를 찾을 수 없습니다.")
    posts_crud.update_post(db=db, db_post=db_post, post_update=_post_update)
"""

@router.get("/list/user/{user_id}")
def post_userlist(user_id: int, db: Session = Depends(get_db)):
     posts = posts_crud.user_postlist(db, user_id=user_id)
     return posts


@router.post("/{username}")
def get_username_post(user_id: int, db: Session = Depends(get_db)):
    username = db.query(Users).get(user_id)
    return username