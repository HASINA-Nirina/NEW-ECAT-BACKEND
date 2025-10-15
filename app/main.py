# app/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from . import db, models, crud, schemas, auth
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI(title="Site ECAT Backend - Step1")

# create tables (for dev only) - better to use Alembic later
models.Base.metadata.create_all(bind=db.engine)

@app.post("/register", response_model=schemas.UserOut)
def register(user_in: schemas.UserCreate, db_s: Session = Depends(db.get_db)):
    # students sign up auto accepted? here we'll set logic:
    # etudiant -> accepted automatically
    # admin_local -> pending, needs admin_super acceptance
    # admin_super -> cannot self-register (preseeded)
    existing = crud.get_user_by_email(db_s, user_in.email) or crud.get_user_by_username(db_s, user_in.username)
    if existing:
        raise HTTPException(status_code=400, detail="Email or username déjà utilisé")

    role = models.RoleEnum(user_in.role)
    created = crud.create_user(db_s, user_in.username, user_in.email, user_in.password, role)
    if role == models.RoleEnum.etudiant:
        created.status = models.AccountStatus.accepted
    elif role == models.RoleEnum.admin_local:
        created.status = models.AccountStatus.pending
    # admin_super registration not allowed via endpoint; check role input
    db_s.add(created)
    db_s.commit()
    db_s.refresh(created)
    return created

@app.post("/login", response_model=schemas.Token)
def login(form_data: schemas.UserCreate, db_s: Session = Depends(db.get_db)):
    # Here reuse schemas.UserCreate to receive username/email+password
    user = crud.get_user_by_username(db_s, form_data.username) or crud.get_user_by_email(db_s, form_data.email)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")
    if user.status != models.AccountStatus.accepted:
        # explicit messages for pending/rejected
        if user.status == models.AccountStatus.pending:
            raise HTTPException(status_code=403, detail="Compte en attente de validation par l'admin super.")
        else:
            raise HTTPException(status_code=403, detail="Compte refusé. Contactez l'administrateur.")
    if not crud.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = auth.create_access_token({"sub": str(user.id), "role": user.role.value})
    return {"access_token": token, "token_type": "bearer"}

# Admin-super endpoint to accept/reject admin_local
@app.post("/admin/validate/{user_id}")
def validate_admin_local(user_id: int, action: str, db_s: Session = Depends(db.get_db)):
    # action: "accept" or "reject"
    user = db_s.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.role != models.RoleEnum.admin_local:
        raise HTTPException(status_code=400, detail="Only admin_local can be validated here")
    if action == "accept":
        user.status = models.AccountStatus.accepted
        db_s.commit()
        # In real app -> send notification/email
        return {"detail": "Compte admin_local accepté et activé."}
    elif action == "reject":
        user.status = models.AccountStatus.rejected
        db_s.commit()
        return {"detail": "Compte admin_local refusé. Raison: non conforme."}
    else:
        raise HTTPException(status_code=400, detail="action must be 'accept' or 'reject'")
