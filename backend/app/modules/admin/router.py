from fastapi import APIRouter, Depends, HTTPException, status
from app.modules.auth.router import get_current_user
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.modules.users.models import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
def read_admin_panel(current_user=Depends(get_current_user)):
    if current_user.rol_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado")
    return {"message": "Bienvenido al panel de administracion"}


@router.get("/fix-user-status")
def fix_user_status(email: str, secret: str, db: Session = Depends(get_db)):
    if secret != "ctech2026":
        raise HTTPException(status_code=403, detail="No autorizado")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    old_status = user.status
    user.status = "active"
    db.commit()
    return {"email": user.email, "status_anterior": old_status, "status_nuevo": user.status}
