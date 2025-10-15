# app/main.py
from fastapi import FastAPI, Depends, HTTPException
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
    # admin_super registration not allowed via endpoint
    db_s.add(created)
    db_s.commit()
    db_s.refresh(created)
    return created


# --- LOGIN CORRIGÉ ---
@app.post("/auth/login")
def login(user: schemas.UserLoginSchema, db_s: Session = Depends(db.get_db)):
    db_user = db_s.query(models.User).filter(models.User.email == user.email).first()

    if not db_user:
        return {"error": "Email invalide"}  # message explicite pour le frontend

    if not crud.verify_password(user.mot_de_passe, db_user.hashed_password):
        return {"error": "Mot de passe incorrect"}

    # Vérifie le rôle pour redirection côté frontend
    return {"role": db_user.role.value}


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
        return {"detail": "Compte admin_local accepté et activé."}
    elif action == "reject":
        user.status = models.AccountStatus.rejected
        db_s.commit()
        return {"detail": "Compte admin_local refusé. Raison: non conforme."}
    else:
        raise HTTPException(status_code=400, detail="action must be 'accept' or 'reject'")
