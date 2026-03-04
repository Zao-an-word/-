from fastapi import  APIRouter


router = APIRouter()

@router.get("/")
def read_root():
    return {"msg": "文思成真 API 正常运行"}

@router.get("/health")
def health_check():
    return {"status": "ok"}