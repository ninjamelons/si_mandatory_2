from fastapi import FastAPI, Header
from pydantic import BaseModel
import uvicorn

from datetime import datetime
import sqlite3

class Address(BaseModel):
	borger_user_id: int
	is_valid: bool

class User(BaseModel):
	user_id: int

db = sqlite3.connect('borger.sqlite')
app = FastAPI()

# User CRUD endpoints
@app.post("/user/create", status_code=201)
async def create_user(user: User):
	# Create user
	query = 'INSERT INTO user (UserId) VALUES (?)'
	db.execute(query, [user.user_id])

	query2 = 'INSERT INTO address (BorgerUserId, IsValid) VALUES (?,?)'
	db.execute(query2, [user.user_id, 1])

	db.commit()

@app.get("/user/read/{user_id}", status_code=200)
async def read_user(user_id: id):
	#Read from one user with id
	query = 'SELECT * FROM user WHERE UserId = ?'
	select = db.execute(query, [user_id])
	db.commit()
	return select

@app.get("/user/readall", status_code=200)
async def read_users():
	#Read from all user
	query = 'SELECT * FROM user'
	select = db.execute(query)
	db.commit()

	people = []
	for row in select:
		people.append({'UserId':row[1], 'CreatedAt':row[2]})

	return people

#This might never be used
#@app.put("/user/update", status_code=200)
#async def update_user():
	#query = 'UPDATE borger SET '
	#db.execute(query, ["", ""])
	#db.commit()
	#return ""

@app.delete("/user/delete/{id}", status_code=200)
async def delete_user(user_id: id):	
	query = 'DELETE * FROM user WHERE Id = ?'
	db.execute(query, [user_id])
	db.commit()
	# Delete corresponding addresses - Cascade is doin' dis for us


# Address CRUD endpoints
@app.post("/address/create/{borger_id}", status_code=201)
async def create_address(borger_user_id: borger_id, address: Address):
	# Cant create address without user.
	queryFind = 'SELECT * user WHERE Id = ?'
	res = db.execute(queryFind, [borger_user_id])

	if(len(res.fetchall()) > 0)
	{
		# Create Address
		query = 'INSERT INTO Address (borger_id, IsValid) VALUES (?,1)'
		db.execute(query,[borger_user_id])
	
		#If address exists, set old isvalid to false
		query2 = 'UPDATE * SET IsValid = false WHERE BorgerUserId = ?'
		db.execute(query2, borger_user_id)
		db.commit()
	}

	return ""

@app.get("/address/read/{id}", status_code=200)
async def read_address(address_id: id):
	#Read from one address with id
	query = 'SELECT * FROM address WHERE Id = ?'
	select = db.execute(query, [address_id])
	db.commit()
	return select

@app.get("/address/read", status_code=200)
async def read_allAddress():
	#Read from all address
	query = 'SELECT * FROM address WHERE Id = ?'
	select = db.execute(query)
	db.commit()

	addresslist = []
	for row in select:
		addresslist.append({'BorgerUserId':row[1], 'CreatedAt':row[2], 'IsValid':row[3]})

	return addresslist

#@app.put("/address/update/{id}/{isValid}", status_code=200)
#async def update_address(is_valid: isValid, user_id: id):
#	query = 'UPDATE * SET IsValid = ? WHERE id = ?'
#	db.execute(query, [is_valid, user_id])
#	db.commit()

	# Updating the address will result in the old one being voided (IsValid = false), and the new one replacing it
#	return ""

@app.delete("/address/delete/{id}", status_code=200)
async def delete_address(address_id: id):
	query = 'DELETE * FROM address WHERE Id = ?'
	db.execute(query, [address_id])
	db.commit()
	

#Start server with uvicorn
if __name__ == "__main__":
	uvicorn.run(app, host="127.0.0.1", port=5004, log_level="info")