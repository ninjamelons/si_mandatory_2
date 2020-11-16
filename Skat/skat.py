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

@app.get("/SkatUser/read/{SkatUser_id}", status_code=200)
async def read_skatUser(skatUser_id: int):
	#Read from one user with id
	query = 'SELECT * FROM SkatUser WHERE Id = ?'
	select = db.execute(query, [skatUser_id])
	db.commit()
	return select


@app.get("/SkatUser/readall", status_code=200)
async def read_skatUsers():
	#Read from all user
	query = 'SELECT * FROM SkatUser'
	select = db.execute(query)
	db.commit()

	people = []
	for row in select:
		people.append({'Id':row[1],'IsActive':row[2],  'CreatedAt':row[3]})

	return people

@app.put("/SkatUser/update", status_code=200)
async def update_skatUser(setActive: int):
	query = 'UPDATE borger SET IsActive = ?'
	db.execute(query, [setActive])
	db.commit()
	
@app.delete("/skatUser/delete/{id}", status_code=200)
async def delete_user(skatUser_id: int):	
	query = 'DELETE * FROM SkatUser WHERE Id = ?'
	db.execute(query, [skatUser_id])
	db.commit()


class SkatYear(BaseModel):
	id : int
	label : str
	startAt: datetime
	endAt: datetime



# SkatYear CRUD endpoints
@app.post("/SkatYear/create", status_code=201)
async def create_SkatYear(skatYear: SkatYear):
	# Create SkatUser
	query = 'INSERT INTO SkatYear (Label, StartAt, EndAt) VALUES (?,?,?)'
	db.execute(query, [skatYear.label, skatYear.startAt, skatYear.endAt])

	

	db.commit()  

 