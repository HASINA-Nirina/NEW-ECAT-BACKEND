# scripts/update-super.py
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # ajoute le répertoire racine au path

from app import db, models, crud

def update_super(new_username: str, new_email: str, new_password: str):
    db_gen = db.get_db()
    db_session = next(db_gen)
    try:
        # Cherche l'utilisateur avec le role admin_super
        user = db_session.query(models.User).filter(models.User.role == models.RoleEnum.admin_super).first()
        if not user:
            print("Aucun admin_super trouvé. Exécute d'abord create-super.py si nécessaire.")
            return

        # Vérifier collision de username/email (autres comptes)
        conflict = db_session.query(models.User).filter(
            ((models.User.username == new_username) | (models.User.email == new_email)) & (models.User.id != user.id)
        ).first()
        if conflict:
            print("Erreur : le username ou l'email est déjà utilisé par un autre compte (id=", conflict.id, ").")
            return

        # Mettre à jour username et email
        user.username = new_username
        user.email = new_email

        # Hacher le nouveau mot de passe avec passlib (bcrypt) via crud.pwd_context
        hashed = crud.pwd_context.hash(new_password)
        user.hashed_password = hashed

        # S'assurer que le statut reste accepté
        user.status = models.AccountStatus.accepted

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        print("✅ admin_super mis à jour :", user.id, user.username, user.email)
    except Exception as e:
        db_session.rollback()
        print("Erreur lors de la mise à jour :", e)
    finally:
        db_session.close()

if __name__ == "__main__":
    # Valeurs demandées
    new_username = "Hasina"
    new_email = "jinxpowder2004@gmail.com"
    new_password = "uy:/p1hvfhasinaC"

    update_super(new_username, new_email, new_password)
