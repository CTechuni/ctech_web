from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.auth.router import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
def read_admin_panel(current_user=Depends(get_current_user)):
    if current_user.rol_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return {"message": "Bienvenido al panel de administracion"}
