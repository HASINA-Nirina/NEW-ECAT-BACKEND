# scripts/create_super.py
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # add project root to path

from app import db, models, crud
from sqlalchemy.orm import Session

def create_super():
    db_gen = db.get_db()
    db_session = next(db_gen)
    try:
        exists = db_session.query(models.User).filter(models.User.role == models.RoleEnum.admin_super).first()
        if exists:
            print("admin_super already exists:", exists.username, exists.email)
            return
        # change credentials below as you want
        username = "adminsuper"
        email = "adminsuper@example.com"
        raw_password = "SuperPassword123"  # change to desired secure pass

        hashed = crud.pwd_context.hash(raw_password)
        user = models.User(username=username, email=email,
                           hashed_password=hashed,
                           role=models.RoleEnum.admin_super,
                           status=models.AccountStatus.accepted)
        db_session.add(user)
        db_session.commit()
        print("admin_super created:", username, email)
    finally:
        db_session.close()

if __name__ == "__main__":
    create_super()
