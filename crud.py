from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import models, schemas, utils, auth


def create_user(db: Session, user: schemas.UserCreate):
    hashed_pwd = auth.get_password_hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_pwd)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_short_url(db: Session, item: schemas.URLCreate, user_id: int = None):
    short_code = utils.generate_short_code()
    while db.query(models.URLItem).filter(models.URLItem.short_code == short_code).first():
        short_code = utils.generate_short_code()

    expires = datetime.utcnow() + timedelta(days=item.ttl_days) if item.ttl_days else None

    db_url = models.URLItem(
        original_url=str(item.url),
        short_code=short_code,
        owner_id=user_id,
        expires_at=expires
    )
    db.add(db_url)
    db.commit()
    db.refresh(db_url)
    return db_url


def get_and_track_url(db: Session, short_code: str):
    db_url = db.query(models.URLItem).filter(models.URLItem.short_code == short_code).first()
    if not db_url:
        return None

    if db_url.expires_at and db_url.expires_at < datetime.utcnow():
        db.delete(db_url)
        db.commit()
        return None

    db_url.clicks += 1
    click_event = models.ClickEvent(url_id=db_url.id)
    db.add(click_event)
    db.commit()
    return db_url


def get_weekly_ranking(db: Session, limit: int = 10):
    week_ago = datetime.utcnow() - timedelta(days=7)

    results = db.query(
        models.URLItem,
        func.count(models.ClickEvent.id).label('weekly_clicks')
    ).join(models.ClickEvent).filter(
        models.ClickEvent.clicked_at >= week_ago
    ).group_by(models.URLItem.id).order_by(
        func.count(models.ClickEvent.id).desc()
    ).limit(limit).all()

    return results