# main.py
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, database, utils, financial
from app.dependencies import get_current_user, require_roles

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

#database session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/profile")
def profile(user = Depends(get_current_user)):
    return {"message": "Access granted", "user": user}

#registartion
@app.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    if len(user.password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail="Password too long (max 72 bytes)")

    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        return {"error": "User already exists"}

    hashed = utils.hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully"}

#login
@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        return {"error": "User not found"}
    if not utils.verify_password(user.password, db_user.password):
        return {"error": "Invalid password"}
    if not db_user.is_active or db_user.is_deleted:
        return {"error": "User inactive or deleted"}
    token = utils.create_access_token({
    "sub": str(db_user.id),   
    "role": db_user.role
})
    return {"access_token": token, "token_type": "bearer"}

#delete
@app.delete("/users/{user_id}")
def delete_user(user_id: int, user = Depends(require_roles(["admin"])), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.id == user_id, models.User.is_deleted == False).first()
    if not db_user:
        return {"error": "User not found"}
    db_user.is_deleted = True
    db.commit()
    return {"message": "User soft-deleted successfully"}

#to include financial.py
app.include_router(financial.router)