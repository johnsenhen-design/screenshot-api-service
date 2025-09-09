from sqlalchemy.orm import Session
import models

def get_user_by_api_key(db: Session, api_key: str):
    """
    Looks up a user in the database by their API key.
    Returns the user object if found and active, otherwise returns None.
    """
    return db.query(models.User).filter(models.User.api_key == api_key, models.User.is_active == True).first()

def get_user_by_email(db: Session, email: str):
    """
    Looks up a user in the database by their email address.
    """
    return db.query(models.User).filter(models.User.email == email).first()