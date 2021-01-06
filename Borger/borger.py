from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uvicorn

from datetime import datetime
import sqlite3

class Address(BaseModel):
	borger_user_id: int
	id: int
	address: str

class BorgerUser(BaseModel):
	user_id: int

db = sqlite3.connect('./Borger/borger.sqlite')
app = FastAPI()

# BorgerUser CRUD endpoints
@app.post("/borgerUser/create", status_code=201)
async def create_borgerUser(borgerUser: BorgerUser):

	# Check if BorgerUserID already exist
	#Read from one user with id
	queryGet = 'SELECT * FROM BorgerUser WHERE UserId = ?'
	select = db.execute(queryGet, [borgerUser.user_id]).fetchone()

	if(select == None):
		# Create BorgerUser
		query = 'INSERT INTO BorgerUser (UserId) VALUES (?)'
		db.execute(query, [borgerUser.user_id])

		query2 = 'INSERT INTO address (BorgerUserId, Address, IsValid) VALUES (?,?,?)'
		db.execute(query2, [borgerUser.user_id, "defualt", 1])
		db.commit()
		return read_BorgerUserFunc(borgerUser.user_id)
	if(len(select) > 0):
		raise HTTPException(status_code=404, detail="The user does already exist!")

def read_BorgerUserFunc(user_id: int):
    #Read from one user with id
	query = 'SELECT * FROM BorgerUser WHERE UserId = ?'
	select = db.execute(query, [user_id]).fetchone()

	if(select == None):
		raise HTTPException(status_code=404, detail="The user does not exist!")
	if(len(select) > 0):
		borgerUser = {select[0], select[1], select[2]}
		return borgerUser

@app.get("/borgerUser/read/{user_id}", status_code=200)
async def read_BorgerUser(user_id: int):
	return read_BorgerUserFunc(user_id)

@app.get("/borgerUser/readall", status_code=200)
async def read_users():
	#Read from all borgerUser
	query = 'SELECT * FROM BorgerUser'
	select = db.execute(query)
	db.commit()

	people = []
	for row in select:
		people.append({'Id':row[0], 'UserId':row[1], 'CreatedAt':row[2]})
	return people

#This might never be used
#@app.put("/borgerUser/update/{user_id}", status_code=200)
#async def update_borgerUser(user_id: int):
	#query = 'UPDATE borgerUser SET UserId = ? WHERE UserId = ?'
	#db.execute(query, [user_id, new_id])
	#db.commit()
	#return ""

@app.delete("/borgerUser/delete/{user_id}", status_code=200)
async def delete_borgerUser(user_id: int):	

	queryGet = 'SELECT * FROM BorgerUser WHERE UserId = ?'
	select = db.execute(queryGet, [user_id]).fetchone()
	
	if(select == None):
    		raise HTTPException(status_code=404, detail="The BorgerUser does not exist!")
	if(len(select) > 0):
		borgerUser = {select[0], select[1], select[2]}

		query = 'DELETE FROM BorgerUser WHERE UserId = ?'
		db.execute(query, [user_id])
		db.commit()
		# Delete corresponding addresses - Cascade is doin' dis for us
		return borgerUser


# Address CRUD endpoints
@app.post("/address/create", status_code=201)
async def create_address(address: Address):
	# Cant create address without user.
	queryFind = 'SELECT * FROM BorgerUser WHERE UserId = ?'
	res = db.execute(queryFind, [address.borger_user_id])

	if(len(res.fetchone()) > 0):
		#set all address false
		query = 'UPDATE address SET IsValid = 0 WHERE BorgerUserId = ?'
		db.execute(query, [address.borger_user_id])
		
		#Create address and set it active
		query2 = 'INSERT INTO Address (BorgerUserId, Address, IsValid) VALUES (?, ?, 1)'
		addressInsert = db.execute(query2,[address.borger_user_id, address.address])
		addressId = addressInsert.lastrowid
		db.commit()
		return read_addressFunc(addressId)
	else:
		raise HTTPException(status_code=400, detail="The UserID was wrong or does not exist!")	

def read_addressFunc(address_id: int):
    #Read from one address with id
	query = 'SELECT * FROM address WHERE Id = ?'
	select = db.execute(query, [address_id]).fetchone()

	if(select == None):
		raise HTTPException(status_code=404, detail="The address does not exist!")
	if(len(select) > 0):
		address = {select[0], select[1], select[2], select[3], select[4]}
		return address		
	
@app.get("/address/read/{address_id}", status_code=200)
async def read_address(address_id: int):
	return read_addressFunc(address_id)


@app.get("/address/readAll", status_code=200)
async def read_allAddress():
	#Read from all address
	query = 'SELECT * FROM address'
	select = db.execute(query)

	addresslist = []
	for row in select:
		addresslist.append({'Id':row[0], 'BorgerUserId':row[1], 'address':row[2], 'CreatedAt':row[3], 'IsValid':row[4]})
	return addresslist

@app.put("/address/update", status_code=200)
async def update_address(address: Address):
	#check if the address exist
	query = 'SELECT * FROM address WHERE Id = ?'
	select = db.execute(query, [address.id]).fetchone()
	
	if(select == None):
		raise HTTPException(status_code=404, detail="The address does not exist!")
	else:
		#set all address false
		query2 = 'UPDATE address SET IsValid = 0 WHERE BorgerUserId = ?'
		db.execute(query2, [address.borger_user_id])
		
		#update address and set it active
		query3 = 'UPDATE address SET Address = ?, IsValid = ? WHERE Id = ?'
		db.execute(query3, [address.address, 1, address.id])
		db.commit()
		return read_addressFunc(address.id)
	
	
@app.delete("/address/delete/{address_id}", status_code=200)
async def delete_address(address_id: int):

	#Read from one address with id
	queryGet = 'SELECT * FROM address WHERE Id = ?'
	select = db.execute(queryGet, [address_id]).fetchone()
	
	if(select == None):
		raise HTTPException(status_code=404, detail="The address does not exist!")
	if(len(select) > 0):
		address = {select[0], select[1], select[2], select[3], select[4]}
		
		#Delete the adresse
		query = 'DELETE FROM address WHERE Id = ?'
		db.execute(query, [address_id])
		db.commit()
		return address
			

#Start server with uvicorn
if __name__ == "__main__":
	uvicorn.run(app, host="127.0.0.1", port=5004, log_level="info")