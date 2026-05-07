from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

import models, schemas, crud
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Modular URL Shortener")

@app.post("/shorten", response_model=schemas.URLInfo)
def shorten_url(item: schemas.URLCreate, db: Session = Depends(get_db)):
    db_url = crud.create_short_url(db, str(item.url))
    return {
        "original_url": db_url.original_url,
        "short_url": f"http://127.0.0.1:8000/{db_url.short_code}"
    }

@app.get("/{short_code}")
def redirect_to_original(short_code: str, db: Session = Depends(get_db)):
    db_url = crud.get_url_by_code(db, short_code)
    if not db_url:
        raise HTTPException(status_code=404, detail="Link not found")
    return RedirectResponse(url=db_url.original_url)