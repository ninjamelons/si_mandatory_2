from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uvicorn

import requests
import json
from datetime import datetime
import sqlite3

class BankUser(BaseModel):
	UserId: int

class Loan(BaseModel):
	BankUserId: int
	Amount : int

class Deposit(BaseModel):
	BankUserId: int
	Amount : int

class Account(BaseModel):
	AccountNo : int
	IsStudent : int
	InterestRate : float
	Amount : int

class Withdraw(BaseModel):
	UserId: int
	Amount : int

db = sqlite3.connect('./Bank/bank.sqlite')
app = FastAPI()

# User CRUD endpoints
@app.post("/bankUser/create", status_code=201)
async def create_bankUser(bankUser: BankUser, account: Account):
	# Create bankUser
	query = 'INSERT INTO BankUser (UserId) VALUES (?)'
	db.execute(query, [bankUser.UserId])

	#get the Id from BankUser to the BankUserId 
	queryGet = 'SELECT * FROM BankUser WHERE UserId = ?'
	select = db.execute(queryGet, [bankUser.UserId]).fetchone()

	query2 = """INSERT INTO Account 
				(BankUserId, AccountNo, IsStudent, InterestRate, Amount)
	            VALUES (?,?,?,?,?)"""
	db.execute(query2, [bankUser.UserId, account.AccountNo, account.IsStudent, account.InterestRate, account.Amount])
	db.commit()

	return "Inserted User"

@app.get("/bankUser/read/{bankUser_id}", status_code=200)
async def read_user(bankUser_id: int):
	#Read from one user with id
	query = 'SELECT * FROM BankUser WHERE Id = ?'
	select = db.execute(query, [bankUser_id])
	db.commit()
	return select.fetchone()

@app.get("/bankUser/readall", status_code=200)
async def read_users():
	#Read from all user
	query = 'SELECT * FROM BankUser'
	select = db.execute(query)
	db.commit()

	bankusers = []
	for row in select:
		bankusers.append({'Id':row[1], 'CreatedAt':row[2], 'ModifiedAt':row[3]})

	return bankusers


@app.delete("/bankUser/delete/{userid}", status_code=200)
async def delete_user(bankUser_id: int):	
	query = 'DELETE * FROM BankUser WHERE UserId = ?'
	db.execute(query, [bankUser_id])
	db.commit()


@app.get("/bankAccount/read/{bankuserid}", status_code=200)
async def read_account(bankuserid: int):
	#Read from one user with id
	query = 'SELECT * FROM Account WHERE BankUserId = ?'
	select = db.execute(query, [bankuserid])
	db.commit()
	return select.fetchone()

# Bank Functionality
@app.post("/add-deposit", status_code=200)
async def deposit_amount(deposit: Deposit):
	if ((deposit.Amount == 0) | (deposit.Amount < 0)):
		raise HTTPException(status_code=422, detail='Deposit needs to be greater than 0')
	
	depositReq = json.dumps({"amount": deposit.Amount})
	interest_added = json.loads(requests.post("http://localhost:7071/api/Interest_Rate", data=depositReq).text)["interest"]

	query = """INSERT INTO Deposit (BankUserId, Amount) VALUES (?,?)"""
	db.execute(query, [deposit.BankUserId, interest_added])

	query2 = """SELECT Amount FROM Account WHERE BankUserId = ?"""
	accountAmount = db.execute(query2, [deposit.BankUserId])

	query3 = """UPDATE Account
				SET Amount = ?
				WHERE BankUserId = ?;"""
	db.execute(query3, [accountAmount.fetchone()[0] + interest_added, deposit.BankUserId])
	db.commit()

	return "Deposited amount: " + str(interest_added)

@app.get("/list-deposits/{bankUserId}", status_code=200)
async def list_deposits(bankUserId: int):
	query = """SELECT * FROM Deposit WHERE BankUserId = (?)"""
	select = db.execute(query, [bankUserId])
	db.commit()

	deposits = []
	for row in select:
		deposits.append({'CreatedAt':row[2], 'Amount':row[3]})

	return deposits

@app.post("/create-loan", status_code=200)
async def create_loan(loan: Loan):
	query = """SELECT Amount FROM Account WHERE BankUserId = ?"""
	c = db.execute(query, [loan.BankUserId])
	db.commit()

	account = c.fetchone()
	
	depositReq = json.dumps({"amount": account[0], "loan": loan.Amount})
	return_code = requests.post("http://localhost:7071/api/Loan_Algorithm", data=depositReq).status_code

	if return_code == 200:
		query2 = """INSERT INTO Loan (BankUserId, Amount) VALUES (?,?)"""
		db.execute(query2, [loan.BankUserId, loan.Amount])
		db.commit()
	else:
		raise HTTPException(status_code=403, detail="Loan greater than 75% of account amount")
	return "Loan amount: " + str(loan.Amount)

@app.post("/pay-loan/{bankUserId}", status_code=200)
async def pay_loan(uid: int):
	query = """SELECT Loan.Amount AS LoanAmount, Account.Amount AS AccAmount
				FROM Loan 
				INNER JOIN Account
				ON Loan.BankUserId = Account.BankUserId
				WHERE Loan.BankUserId = ?;"""
	loanValues = db.execute(query, [uid]).fetchone()
	db.commit()

	loanAmount = loanValues[0]
	accAmount = loanValues[1]
	
	if loanAmount > accAmount:
		raise HTTPException(status_code=422, detail="Loan greater than account amount")
	else:
		accAmount -= loanAmount
		query2 = """UPDATE Loan
					SET Amount = 0
					WHERE BankUserId = ?;"""
		db.execute(query2, [uid])

		query3 = """UPDATE Account
					SET Amount = ?
					WHERE BankUserId = ?;"""
		db.execute(query3, [accAmount, uid])

		db.commit()
	return "Loan Paid"

@app.get("/list-loans/{uid}", status_code=200)
async def list_loans(uid: int):
	#Read all loans
	query = 'SELECT * FROM Loan WHERE BankUserId = ?'
	select = db.execute(query, [uid])
	db.commit()

	loans = []
	for row in select:
		loans.append({'BankUserId':row[1], 'CreatedAt':row[2], 'ModifiedAt':row[3], 'Amount':row[4]})

	return loans

## The body of that request should contain an amount and a UserId(Not BankUserId, not SkatUserId)
## Subtract (if possible) the amount from that users account. Throw an error otherwise.
@app.post("/withdrawal-money", status_code=200)
async def withdraw_money(withdrawModel: Withdraw):
	query = 'SELECT Amount FROM Account WHERE Id = ?'
	selectAccountAmount = db.execute(query, withdrawModel.UserId).fetchone()

	if (withdrawModel.Amount > selectAccountAmount[0]):
		raise HTTPException(status_code=422, detail="withdraw amount is greater than account amount")
	
	else:
		query2 = 'UPDATE Account SET amount = ? WHERE Id = ?'
		db.execute(query2, [selectAccountAmount[0] - withdrawModel.Amount, withdrawModel.UserId])
		db.commit()
	return "Withdraw: " + str(withdrawModel.Amount)

#Start server with uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5003, log_level="info")