from fastapi import FastAPI, Header
from pydantic import BaseModel
import uvicorn

from datetime import datetime
import sqlite3

class SkatUser(BaseModel):
	id : int
	Userid: int

db = sqlite3.connect('skat.sqlite')
app = FastAPI()

# SkatUser CRUD endpoints
@app.post("/SkatUser/create", status_code=201)
async def create_SkatUser(skatUser: SkatUser):
	# Create SkatUser
	query = 'INSERT INTO BankUser (UserId, IsActive) VALUES (?)'
	db.execute(query, [skatUser.Userid, 1])

	db.commit()  

 