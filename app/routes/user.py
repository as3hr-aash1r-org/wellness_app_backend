from fastapi import APIRouter

router = APIRouter(prefix="/api",tags=["Users"])

@router.get("/")
def test_route():
    return "hello tested"