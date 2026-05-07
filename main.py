from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import List
from fastapi import Response

import models, schemas, crud, auth
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Pro URL Shortener")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204)


@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db, user)


@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = auth.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/shorten", response_model=schemas.URLInfo)
def shorten_url(item: schemas.URLCreate, db: Session = Depends(get_db),
                current_user: models.User = Depends(auth.get_current_user)):
    db_url = crud.create_short_url(db, item, user_id=current_user.id)
    return {
        "original_url": db_url.original_url,
        "short_url": f"http://127.0.0.1:8000/{db_url.short_code}",
        "clicks": db_url.clicks,
        "expires_at": db_url.expires_at
    }


@app.get("/ranking/weekly", response_model=List[schemas.URLRanking])
def get_ranking(db: Session = Depends(get_db)):
    ranking = crud.get_weekly_ranking(db)
    return [
        {
            "short_url": f"http://127.0.0.1:8000/{url.short_code}",
            "original_url": url.original_url,
            "weekly_clicks": clicks
        } for url, clicks in ranking
    ]


@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    db_url = crud.get_and_track_url(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found or expired")
    return RedirectResponse(url=db_url.original_url)