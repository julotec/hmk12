from fastapi import FastAPI, Depends, Path, Query, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel,Field
from datetime import datetime
from db import get_db, Contact
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from auth import create_access_token, create_refresh_token, get_current_user, Hash, get_email_form_refresh_token

app = FastAPI()
hash_handler = Hash()
security = HTTPBearer()

@app.get("/contacts/all")
def get_all_contacts(session: Session = Depends(get_db)):
    contacts = session.query(Contact).all()
    return contacts


@app.get("/contacts/{user_id}")
async def read_contacts(user_id: int = Path(
    description = "The ID of the contact to get", gt = 0, le = 10
    ),
    skip: int = 0,
    limit: int= Query(default = 10, le = 100, ge = 10),
    session: Session = Depends(get_db)
):

    result = session.query(Contact).get(user_id)
    return result



class User(BaseModel):
    user_id: int = Field(default = 1, ge = 1)
    name: str
    surname:str
    mail_address: str
    phone: int
    birth_date: datetime
    additional_info: Optional[str] = None
    password: str


@app.post("/contacts/")
def create_new_contact(contact: User, session=Depends(get_db)):
    
    session.add(
        Contact(
            id=contact.user_id,
            first_name=contact.name,
            last_name=contact.surname,
            email=contact.mail_address,
            phone_number=contact.phone,
            birth_date=contact.birth_date,
            additional_data=contact.additional_info,
            password = contact.password,
            )
        )
    session.commit()
    return contact
    




@app.put("/contacts/{user_id}")
def update_contact(
    user_id: int,
    updated_contact: User,
    session: Session = Depends(get_db)
):
    db_contact = session.query(Contact).get(user_id)

    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    db_contact.first_name = updated_contact.name
    db_contact.last_name = updated_contact.surname
    db_contact.email = updated_contact.mail_address
    db_contact.phone_number = updated_contact.phone
    db_contact.birth_date = updated_contact.birth_date
    db_contact.additional_data = updated_contact.additional_info
    

    session.commit()

    return {"message": "Contact updated successfully"}

@app.delete("/contacts/{user_id}")
def delete_contact(
    user_id: int,
    session: Session = Depends(get_db)
):
    db_contact = session.query(Contact).get(user_id)

    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")

    session.delete(db_contact)
    session.commit()

    return {"message": "Contact deleted successfully"}
    



@app.post("/signup")
async def signup(body: User, db: Session = Depends(get_db)):
    exist_user = db.query(Contact).filter(Contact.email == body.mail_address).first()

    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    new_user = User(email=body.name, password=hash_handler.get_password_hash(body.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"new_user": new_user.email}


@app.post("/login")
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(Contact).filter(Contact.email == body.mail_address).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not hash_handler.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    # Generate JWT
    access_token = await create_access_token(data={"sub": user.email})
    refresh_token = await create_refresh_token(data={"sub": user.email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@app.get('/refresh_token')
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    email = await get_email_form_refresh_token(token)
    user = db.query(User).filter(User.email == email).first()
    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    access_token = await create_access_token(data={"sub": email})
    refresh_token = await create_refresh_token(data={"sub": email})
    user.refresh_token = refresh_token
    db.commit()
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}


@app.get("/secret")
async def read_item(current_user: User = Depends(get_current_user)):
    return {"message": 'secret router', "owner": current_user.email}