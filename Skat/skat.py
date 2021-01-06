from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uvicorn

import requests
from datetime import datetime
import sqlite3
import json

class SkatUser(BaseModel):
	UserId: int

class SkatYear(BaseModel):
	label : str
	startDate: datetime
	endDate: datetime

class Tax(BaseModel):
	UserId: int
	Amount: int

db = sqlite3.connect('./Skat/skat.sqlite')
app = FastAPI()

# SkatUser CRUD endpoints
@app.post("/SkatUser/create", status_code=201)
async def create_SkatUser(skatUser: SkatUser):
	
	# Check if UserID already exist
	#Read from one user with id
	queryGet = 'SELECT * FROM SkatUser WHERE UserId = ?'
	select = db.execute(queryGet, [skatUser.UserId]).fetchone()

	if(select == None):
		# Create SkatUser
		query = 'INSERT INTO SkatUser (UserId, IsActive) VALUES (?,?)'
		db.execute(query, [skatUser.UserId, 1])
		db.commit()
		return read_skatUserFunc(skatUser.UserId)
	if(len(select) > 0):
		raise HTTPException(status_code=404, detail="The user does already exist!")

def read_skatUserFunc(skatUser_id: int):
    #Read from one user with id
	query = 'SELECT * FROM SkatUser WHERE UserId = ?'
	select = db.execute(query, [skatUser_id]).fetchone()

	if(select == None):
		raise HTTPException(status_code=404, detail="The user does not exist!")
	if(len(select) > 0):
		skatUser = {select[0], select[1], select[2], select[3]}
		return skatUser

@app.get("/SkatUser/read/{SkatUser_id}", status_code=200)
async def read_skatUser(skatUser_id: int):
	return read_skatUserFunc(skatUser_id)
	

@app.get("/SkatUser/readall", status_code=200)
async def read_skatUsers():
	#Read from all user
	query = 'SELECT * FROM SkatUser'
	select = db.execute(query)
	
	people = []
	for row in select:
		people.append({'Id':row[0], 'UserId':row[1], 'CreatedAt':row[2], 'IsActive':row[3]})
	return people

@app.put("/SkatUser/update", status_code=200)
async def update_skatUser(setActive: int, UserId: int):
	#check if the SkatUser exist
	query = 'SELECT * FROM SkatUser WHERE UserId = ?'
	select = db.execute(query, [UserId]).fetchone()

	if(select == None):
		raise HTTPException(status_code=404, detail="The SkatUser does not exist!")
	if((setActive == 1) or (setActive ==0)): 
		query2 = 'UPDATE SkatUser SET IsActive = ? WHERE UserId = ?'
		db.execute(query2, [setActive, UserId])
		db.commit()
		return read_skatUserFunc(UserId)
	else:
		raise HTTPException(status_code=404, detail="The is active can only be a 1 or 0!")
		
	
@app.delete("/skatUser/delete/{skatUse_id}", status_code=200)
async def delete_skatuUser(skatUser_id: int):	
	
	#Read from one SkatUser with id
	query = 'SELECT * FROM SkatUser WHERE UserId = ?'
	select = db.execute(query, [skatUser_id]).fetchone()
	
	if(select == None):
		raise HTTPException(status_code=404, detail="The address does not exist!")
	if(len(select) > 0):
		skatUser = {select[0], select[1], select[2], select[3]}
		
		#Delete the skatUser
		query = 'DELETE FROM SkatUser WHERE Id = ?'
		db.execute(query, [skatUser_id])
		db.commit()
		return skatUser

# SkatYear CRUD endpoints
@app.post("/SkatYear/create", status_code=201)
async def create_SkatYear(skatYear: SkatYear):
	# Create SkatUser
	query = 'INSERT INTO SkatYear (Label, StartDate, EndDate) VALUES (?,?,?)'
	c = db.execute(query, [skatYear.label, skatYear.startDate, skatYear.endDate])
	
	skatYearId = c.lastrowid

	query = """SELECT Id, UserId FROM SkatUser"""
	users = db.execute(query)

	for row in users:
		query2 = 'INSERT INTO SkatUserYear (SkatUserId, SkatYearId, UserId, isPaid, Amount) VALUES (?,?,?,?,?)'
		db.execute(query2, [row[0], skatYearId, row[1], 0, 0])

	db.commit()  
	return read_skatYearFunc(skatYearId)

def read_skatYearFunc(skatYear_id: int):
	#Read from one user with id
	query = 'SELECT * FROM SkatYear WHERE Id = ?'
	select = db.execute(query, [skatYear_id]).fetchone()

	if(select == None):
		raise HTTPException(status_code=404, detail="The user does not exist!")
	if(len(select) > 0):
		skatYear ={select[0], select[1], select[2], select[3], select[4], select[5]}
		return skatYear

@app.get("/SkatYear/read/{SkatYear_id}", status_code=200)
async def read_skatYear(skatYear_id: int):
	return read_skatYearFunc(skatYear_id)

@app.get("/SkatYear/readall", status_code=200)
async def read_skatYears():
	#Read from all user
	query = 'SELECT * FROM SkatYear'
	select = db.execute(query)
	
	skatYears = []
	for row in select:
		skatYears.append({'Id':row[0], 'Label':row[1], 'CreatedAt':row[2], 'ModifiedAt':row[3], 'StartAt':row[4], 'EndAt':row[5]})

	return skatYears

@app.put("/SkatYear/update", status_code=200)
async def update_skatYear(label: str, modifiedAt: datetime, id: int):
	
	#check if the address exist
	query = 'SELECT * FROM SkatYear WHERE Id = ?'
	select = db.execute(query, [id]).fetchone()
	
	if(select == None):
		raise HTTPException(status_code=404, detail="The address does not exist!")
	else:
		query = 'UPDATE skatYear SET Label = ?, ModifiedAt = ? WHERE Id = ?'
		db.execute(query, [label, modifiedAt, id])
		db.commit()
		return read_skatYearFunc(id)


@app.delete("/skatYear/delete/{id}", status_code=200)
async def delete_skatYear(skatYear_id: int):	

	#Read from one user with id
	query = 'SELECT * FROM SkatYear WHERE Id = ?'
	select = db.execute(query, [skatYear_id]).fetchone()

	if(select == None):
		raise HTTPException(status_code=404, detail="The skatYear does not exist!")
	else:
		skatUser = {select[0], select[1], select[2], select[3]}
		
		query = 'DELETE * FROM SkatYear WHERE Id = ?'
		db.execute(query, [skatYear_id])
		db.commit()
		# Delete corresponding SkatUserYear - Cascade is doin' dis for us
		return skatUser

@app.post("/pay-taxes", status_code=200)
async def pay_taxes(tax: Tax):
	#Check if user paid taxes (if SkatUserYear.Amount > 0) ? Why not IsPaid == true?
	#Call Tax Calculator - SkatUserYear.Amount = response.sum & IsPaid = true
	#Call BankAPI/subtractMoneyFromAccount - Body: UserId, Amount

	query = "SELECT Amount FROM SkatUserYear WHERE UserId = ? ORDER BY Id DESC;" #Order by DESC to get the latest entry
	c = db.execute(query, [tax.UserId])
	
	skatuseryear = c.fetchone() #Fetch latest row
	
	if(skatuseryear == None):
		raise HTTPException(status_code=404, detail="The skatYear does not exist!")
	if skatuseryear[0] <= 0:
		obj = {'money': tax.Amount}
		response = requests.post("http://localhost:7071/api/Skat_Tax_Calculator", data=json.dumps(obj))
		if response.status_code == 200:
			query2 = "UPDATE SkatUserYear SET Amount = ?, IsPaid = ? WHERE UserId = ?"
			db.execute(query2, [(response.json()['tax_money']), 1, tax.UserId])
			db.commit()

			obj2 = {'UserId': tax.UserId, 'Amount': response.json()['tax_money']}
			response2 = requests.post("http://localhost:5003/withdrawal-money", data=json.dumps(obj2))
			return response.json()['tax_money']
	return "You have already paid"

#Start server with uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5002, log_level="info")