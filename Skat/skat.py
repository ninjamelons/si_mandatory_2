from fastapi import FastAPI, Header
from pydantic import BaseModel
import uvicorn

import requests
from datetime import datetime
import sqlite3

class SkatUser(BaseModel):
	id : int
	Userid: int

db = sqlite3.connect('./Skat/skat.sqlite')
app = FastAPI()

# SkatUser CRUD endpoints
@app.post("/SkatUser/create", status_code=201)
async def create_SkatUser(skatUser: SkatUser):
	# Create SkatUser
	query = 'INSERT INTO SkatUser (UserId, IsActive) VALUES (?,?)'
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
		people.append({'Id':row[1], 'IsActive':row[2], 'CreatedAt':row[3]})

	return people

@app.put("/SkatUser/update", status_code=200)
async def update_skatUser(setActive: int):
	query = 'UPDATE SkatUser SET IsActive = ?'
	db.execute(query, [setActive])
	db.commit()
	
@app.delete("/skatUser/delete/{id}", status_code=200)
async def delete_skatuUser(skatUser_id: int):	
	query = 'DELETE * FROM SkatUser WHERE Id = ?'
	db.execute(query, [skatUser_id])
	db.commit()


class SkatYear(BaseModel):
	id : int
	label : str
	startAt: datetime
	endAt: datetime

class SkatUserYear(BaseModel):
	id : int
	skatUserId : int
	userId : int
	isPaid : int
	amount : int

# SkatYear CRUD endpoints
@app.post("/SkatYear/create", status_code=201)
async def create_SkatYear(skatYear: SkatYear, skatUserYear: SkatUserYear):
	# Create SkatUser
	query = 'INSERT INTO SkatYear (Label, StartAt, EndAt) VALUES (?,?,?)'
	db.execute(query, [skatYear.label, skatYear.startAt, skatYear.endAt])

	queryGet = 'SELECT Id FROM SkatYear WHERE Label = ?'
	find = db.execute(queryGet, [SkatYear.label])

	query2 = 'INSERT INTO SkatUserYear (SkatUserId, SkatYearId, UserId, isPaid, Amount) VALUES (?,?,?,?,?)'
	db.execute(query2, [skatUserYear.skatUserId, find.Id, skatUserYear.UserId, skatUserYear.isPaid, skatUserYear.amount])

	db.commit()  


@app.get("/SkatYear/read/{SkatYear_id}", status_code=200)
async def read_skatYear(skatYear_id: int):
	#Read from one user with id
	query = 'SELECT * FROM SkatYear WHERE Id = ?'
	select = db.execute(query, [skatYear_id])
	db.commit()
	return select


@app.get("/SkatYear/readall", status_code=200)
async def read_skatYears():
	#Read from all user
	query = 'SELECT * FROM SkatYear'
	select = db.execute(query)
	db.commit()

	skatYears = []
	for row in select:
		skatYears.append({'Id':row[1],'Label':row[2], 'CreatedAt':row[3], 'ModifiedAt':row[4], 'StartAt':row[5], 'EndAt':row[6]})

	return skatYears

@app.put("/SkatYear/update", status_code=200)
async def update_skatYear(label: str, modifiedAt: datetime, id: int):
	query = 'UPDATE skatYear SET Label = ?, ModifiedAt = ? WHERE Id = ?'
	db.execute(query, [label, modifiedAt, id])
	db.commit()

@app.delete("/skatYear/delete/{id}", status_code=200)
async def delete_skatYear(skatYear_id: int):	
	query = 'DELETE * FROM SkatYear WHERE Id = ?'
	db.execute(query, [skatYear_id])
	db.commit()
	# Delete corresponding SkatUserYear - Cascade is doin' dis for us


class Tax(BaseModel):
	UserId: int
	Amount: int

@app.post("/pay-taxes", status_code=200)
async def pay_taxes(tax: Tax):
	#Check if user paid taxes (if SkatUserYear.Amount > 0) ???? Why not IsPaid == true??
	#Call Tax Calculator - SkatUserYear.Amount = response.sum & IsPaid = true
	#Call BankAPI/subtractMoneyFromAccount - Body: UserId, Amount

	query = "SELECT Amount FROM SkatUserYear WHERE UserId = '?' ORDER BY Id DESC;" #Order by DESC to get the latest entry
	c = db.execute(query, [tax.UserId])
	db.commit()
	skatuseryear = c.fetchone() #Fetch latest row

	if skatuseryear.Amount <= 0:
		obj = {'amount': skatuseryear.Amount}
		response = requests.post("http://localhost:7071/api/Skat_Tax_Calculator", data=json.dumps(obj))
		if response.status_code == 200:
			query2 = "UPDATE SkatUserYear SET Amount = ?, IsPaid = ? WHERE UserId = ?"
			db.execute(query, [response.tax_money, 1, tax.UserId])
			db.commit()

			obj2 = {'UserId': tax.UserId, 'Amount': response.tax_money}
			response2 = requests.post("http://localhost:5003/withdrawal-money", data=json.dumps(obj2))

#Start server with uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5002, log_level="info")