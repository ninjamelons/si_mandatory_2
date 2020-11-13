from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uvicorn

import requests
from datetime import datetime
import sqlite3

class BankUser(BaseModel):
	id : int
	Userid: int

class Loan(BaseModel):
	BankUserid: int
	Amount : int

class Deposit(BaseModel):
	id : int
	BankUserid: int
	Amount : int

class Account(BaseModel):
	id : int
	BankUserid: int
	IsStudent : bool
	InterestRate : float
	Amount : int

db = sqlite3.connect('bank.sqlite')
app = FastAPI()

# User CRUD endpoints
@app.post("/bankUser/create", status_code=201)
async def create_bankUser(bankUser: BankUser, account: Account, loan: Loan):
	# Create bankUser
	query = 'INSERT INTO BankUser (UserId) VALUES (?)'
	db.execute(query, [bankUser.Userid])

	#get the Id from BankUser to the BankUserId 
	queryGet = 'SELECT * BankUser WHERE UserId = ?'
	select = db.execute(queryGet, [bankUser.Userid]) 

	query2 = """INSERT INTO Account 
				(BankUserId, AccountNo, IsStudent, InterestRate, Amount)
	            VALUES (?,?,?,?,?)"""
	db.execute(query2, [select.Id ,account.AccountNo, account.IsStudent, account.InterestRate, account.Amount])
	 
	query3 = 'INSERT INTO Loan (Userid, Amount) VALUES (?,?)'
	db.execute(query3, [select.Id loan.Amount])

	db.commit()      


@app.get("/bankUser/read/{bankUser_id}", status_code=200)
async def read_user(bankUser_id: id):
	#Read from one user with id
	query = 'SELECT * FROM BankUser WHERE Id = ?'
	select = db.execute(query, [bankUser_id])
	db.commit()
	return select


@app.get("/bankUser/readall", status_code=200)
async def read_users():
	#Read from all user
	query = 'SELECT * FROM BankUser'
	select = db.execute(query)
	db.commit()

	people = []
	for row in select:
		people.append({'Id':row[1], 'CreatedAt':row[2]})

	return people


@app.delete("/bankUser/delete/{id}", status_code=200)
async def delete_user(bankUser_id: id):	
	query = 'DELETE * FROM user WHERE Id = ?'
	db.execute(query, [bankUser_id])
	db.commit()


@app.get("/bankAccount/read/{account_id}", status_code=200)
async def read_account(account_id: id):
	#Read from one user with id
	query = 'SELECT * FROM Account WHERE Id = ?'
	select = db.execute(query, [account_id])
	db.commit()
	return select


# Bank Functionality
class Deposit(BaseModel):
	BankUserId: int
	Amount: int

@app.post("/add-deposit", status_code=200)
async def deposit_amount(deposit: Deposit):
	if deposit.Amount == null || deposit.Amount < 0:
        raise HTTPException(status_code=422, detail="Deposit needs to be greater than 0")
	interest_added = deposit.Amount	#CALL AZURE FUNCTION SOMEHOW

	#response = requests.get("localhost:7073/Interest_Rate")

	query = """INSERT INTO Deposit (BankUserId, Amount) VALUES (?,?)"""
	db.execute(query, [deposit.BankUserId, interest_added])
	db.commit()

@app.get("/list-deposits/{bankuserid}", status_code=200)
async def list_deposits(bui: bankuserid):
	query = """SELECT * FROM Deposit WHERE BankUserId = (?)"""
	db.execute(query, [bui])
	db.commit()

	deposits = []
	for row in select:
		deposits.append({'CreatedAt':row[2], 'Amount':row[3})

	return deposits

@app.post("/create-loan", status_code=200)
async def create_loan(loan: Loan):
	query = """SELECT Amount FROM Account WHERE BankUserId = '?';"""
	c = db.execute(query, [loan.BankUserId])
	db.commit()

	account = c.fetchone()
	
	return_code = 0#CALL AZURE FUNCTION SOMEHOW
	#response = requests.get("localhost:7073/Loan_Algorithm")

	if return_code == 200:
		query2 = """INSERT INTO Loan () VALUES ()"""
		db.execute(query2, [])
		db.commit()
	else:
        raise HTTPException(status_code=403, detail="Loan greater than 75% of account amount")

@app.post("/pay-loan/{bankuserid}", status_code=200)
async def pay_loan(uid: bankuserid):
	query = """SELECT (Loan.Amount as LoanAmount, Account.Amount as AccAmount)
				FROM Loan 
				INNER JOIN Account
				ON Loan.BankUserId = Account.BankUserId
				WHERE Loan.BankUserId = '?';"""
	c = db.execute(query, [uid])
	db.commit()

	loanAmount = c.fetchone()['LoanAmount']
	accAmount = c.fetchone()['Amount']
	
	if loanAmount > accAmount:
        raise HTTPException(status_code=422, detail="Loan greater than account amount")
	else:
		accAmount -= loanAmount
		query2 = """UPDATE Loan
					SET Amount = 0
					WHERE BankUserId = '?';"""
		db.execute(query2, [uid])

		query3 = """UPDATE Account
					SET Amount = '?'
					WHERE BankUserId = '?';"""
		db.execute(query3, [accAmount, uid])

		db.commit()

@app.get("/list-loans", status_code=200)
async def list_loans():
	#Read all loans
	query = 'SELECT * FROM Loan'
	db.execute(query)
	select = db.commit()

	loans = []
	for row in select:
		loans.append({'BankUserId':row[1], 'CreatedAt':row[2], 'ModifiedAt':row[3], 'Amount':row[4]})

	return loans

class Withdraw(BaseModel):
	UserId: int
	Amount : int
	## The body of that request should contain an amount and a UserId(Not BankUserId, not SkatUserId)
    ## Subtract (if possible) the amount from that users account. Throw an error otherwise.
@app.get("withdrawal-money", status_code=200)
async def withdraw-money(withdrawModel: Withdraw):
	query = 'SELECT Amount FROM Account WHERE Id = ?'
	selectAccountAmount = db.execute(query, withdrawModel.UserId)

	íf (withdrawModel.Amount > selectAccountAmount.fetchone()['Amount'])
	{
		raise HTTPException(status_code=422, detail="withdraw amount is greater than account amount")
	}
	else
	{
		query2 = 'UPDATE Account SET amount = ? WHERE Id = ?'
		db.execute(query2, [selectAccountAmount.fetchone()['Amount'] - withdrawModel.Amount, withdrawModel.UserId])
	}	
	