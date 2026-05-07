from sqlalchemy.orm import Session
import models, utils

def get_url_by_code(db: Session, short_code: str):
    return db.query(models.URLItem).filter(models.URLItem.short_code == short_code).first()

def get_url_by_original(db: Session, original_url: str):
    return db.query(models.URLItem).filter(models.URLItem.original_url == original_url).first()

def create_short_url(db: Session, url: str):
    existing = get_url_by_original(db, url)
    if existing:
        return existing

    short_code = utils.generate_short_code()
    while get_url_by_code(db, short_code):
        short_code = utils.generate_short_code()

    db_url = models.URLItem(original_url=url, short_code=short_code)
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url