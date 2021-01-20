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
	BankUserId: int
	Amount : int

db = sqlite3.connect('./Bank/bank.sqlite')
app = FastAPI()

# User CRUD endpoints
@app.post("/bankUser/create", status_code=201)
async def create_bankUser(bankUser: BankUser, account: Account):
	
	# Check if BankUser with UserID already exist
	#Read from one user with id
	query = 'SELECT * FROM BankUser WHERE UserId = ?'
	select = db.execute(query, [bankUser.UserId]).fetchone()

	if(select == None):
		# Create BankUser
		query = 'INSERT INTO BankUser (UserId) VALUES (?)'
		db.execute(query, [bankUser.UserId])

		#get the Id from BankUser to the BankUserId 
		queryGet = 'SELECT * FROM BankUser WHERE UserId = ?'
		bu = db.execute(queryGet, [bankUser.UserId]).fetchone()
		returnBankUser = {
			'Id':bu[0],
			'UserId':bu[1],
			'CreatedAt':bu[2],
			'ModifiedAt':bu[3]}

		query2 = """INSERT INTO Account 
					(BankUserId, AccountNo, IsStudent, InterestRate, Amount)
					VALUES (?,?,?,?,?)"""
		accountInsert = db.execute(query2, [bu[0], account.AccountNo, account.IsStudent, account.InterestRate, account.Amount])
		accountId = accountInsert.lastrowid

		query3 = 'SELECT * FROM Account WHERE Id = ?'
		acc = db.execute(query3, [accountId]).fetchone()
		returnAccount = {
			'Id':acc[0],
			'BankUserId':acc[1],
			'AccountNo':acc[2],
			'IsStudent':acc[3],
			'CreatedAt':acc[4],
			'ModifiedAt':acc[5],
			'InterestRate':acc[6],
			'Amount':acc[7]
			}
	
		returnUser = {'BankUser':returnBankUser, 'Account':returnAccount}
		db.commit()
		return returnUser
	if(len(select) > 0):
		raise HTTPException(status_code=404, detail="The user does already exist!")
	

@app.get("/bankUser/read/{bankUser_id}", status_code=200)
async def read_user(bankUser_id: int):
	#Read from one user with id
	query = 'SELECT * FROM BankUser WHERE Id = ?'
	select = db.execute(query, [bankUser_id]).fetchone()
	if select == None:
		raise HTTPException(status_code=404, detail='BankUser with Id not found')
	returnBankUser = {
		'Id':select[0],
		'UserId':select[1],
		'CreatedAt':select[2],
		'ModifiedAt':select[3]
		}
	
	return returnBankUser

@app.get("/bankUser/readall", status_code=200)
async def read_users():
	#Read from all user
	query = 'SELECT * FROM BankUser'
	select = db.execute(query)

	bankusers = []
	for row in select:
		bankusers.append({'Id':row[0], 'UserId':row[1],'CreatedAt':row[2], 'ModifiedAt':row[3]})

	return bankusers

@app.delete("/bankUser/delete/{bankUser_id}", status_code=200)
async def delete_user(bankUser_id: int):
	#delete with BankUser Id
	query = 'SELECT * FROM BankUser WHERE Id = ?'
	bu = db.execute(query, [bankUser_id]).fetchone()
	if bu == None:
		raise HTTPException(status_code=404, detail='BankUser with Id not found')
	
	returnBankUser = {
		'Id':bu[0],
		'UserId':bu[1],
		'CreatedAt':bu[2],
		'ModifiedAt':bu[3]}
	
	query2 = 'SELECT * FROM Account WHERE BankUserId = ?'
	acc = db.execute(query2, [bankUser_id]).fetchone()
	if acc == None:
		raise HTTPException(status_code=404, detail='Account with BankUserId not found')
	returnAccount = {
		'Id':acc[0],
		'BankUserId':acc[1],
		'AccountNo':acc[2],
		'IsStudent':acc[3],
		'CreatedAt':acc[4],
		'ModifiedAt':acc[5],
		'InterestRate':acc[6],
		'Amount':acc[7]
		}
	
	query3 = 'DELETE FROM BankUser WHERE Id = ?'
	query4 = 'DELETE FROM Account WHERE BankUserId = ?'
	deleteBU = db.execute(query3, [bankUser_id])
	deleteAcc = db.execute(query4, [bankUser_id])
	db.commit()

	returnUser = {'BankUser':returnBankUser, 'Account':returnAccount}
	return returnUser

@app.get("/bankAccount/read/{bankUser_id}", status_code=200)
async def read_account(bankUser_id: int):
	#Read from one user with id
	query = 'SELECT * FROM Account WHERE BankUserId = ?'
	acc = db.execute(query, [bankUser_id]).fetchone()
	if acc == None:
		raise HTTPException(status_code=404, detail='Account with BankUserId not found')
	returnAccount = {
		'Id':acc[0],
		'BankUserId':acc[1],
		'AccountNo':acc[2],
		'IsStudent':acc[3],
		'CreatedAt':acc[4],
		'ModifiedAt':acc[5],
		'InterestRate':acc[6],
		'Amount':acc[7]
		}
	
	return returnAccount

# Bank Functionality
@app.post("/add-deposit", status_code=200)
async def deposit_amount(deposit: Deposit):
	if ((deposit.Amount == 0) | (deposit.Amount < 0)):
		raise HTTPException(status_code=422, detail='Deposit needs to be greater than 0')

	# Get Account current Amount and InterestRate
	query = """SELECT Amount, InterestRate FROM Account WHERE BankUserId = ?"""
	account = db.execute(query, [deposit.BankUserId]).fetchone()
	if account == None:
		raise HTTPException(status_code=404, detail='Account with BankUserId not found')

	accAmount = account[0]
	accInterest = account[1]
	
	# Calculated deposited amount based on InterestRate
	depositReq = json.dumps({"amount": deposit.Amount, "interest_rate": accInterest})
	interest_added = json.loads(requests.post("http://localhost:7071/api/Interest_Rate", data=depositReq).text)["interest"]

	# Insert deposited amount into Deposit
	query2 = """INSERT INTO Deposit (BankUserId, Amount) VALUES (?,?)"""
	db.execute(query2, [deposit.BankUserId, interest_added])

	# Update current balance (amount += deposit)
	query3 = """UPDATE Account
				SET Amount = ?
				WHERE BankUserId = ?;"""
	db.execute(query3, [accAmount + interest_added, deposit.BankUserId])
	db.commit()

	returnObj = {
		'BankUserId':deposit.BankUserId,
		'DepositAmount':interest_added,
		'CurrentBalance':(accAmount+interest_added)
		}
	return returnObj

@app.get("/list-deposits/{bankUser_id}", status_code=200)
async def list_deposits(bankUser_id: int):
	query = """SELECT * FROM Deposit WHERE BankUserId = (?)"""
	select = db.execute(query, [bankUser_id])
	db.commit()

	deposits = []
	for row in select:
		deposits.append({'CreatedAt':row[2], 'Amount':row[3]})

	return deposits

#Creates a new loan if a 
@app.post("/create-loan", status_code=200)
async def create_loan(loan: Loan):
	query = """SELECT Amount FROM Account WHERE BankUserId = ?"""
	c = db.execute(query, [loan.BankUserId]).fetchone()
	if c == None:
		raise HTTPException(status_code=404, detail='Account with BankUserId not found')

	accAmount = c[0]
	
	depositReq = json.dumps({"amount": accAmount, "loan": loan.Amount})
	return_code = requests.post("http://localhost:7071/api/Loan_Algorithm", data=depositReq).status_code

	loanId = 0
	if return_code == 200:
		# Insert into Loans table
		query2 = """INSERT INTO Loan (BankUserId, Amount) VALUES (?,?)"""
		loanId = db.execute(query2, [loan.BankUserId, loan.Amount]).lastrowid

		# Update current balance (amount += deposit)
		query3 = """UPDATE Account
					SET Amount = ?
					WHERE BankUserId = ?;"""
		db.execute(query3, [accAmount + loan.Amount, loan.BankUserId])

		db.commit()
	else:
		raise HTTPException(status_code=403, detail="Loan greater than 75% of account amount")

	returnObj = {
		'LoanId': loanId,
		'BankUserId': loan.BankUserId,
		'LoanAmount': loan.Amount,
		'CurrentBalance': (accAmount + loan.Amount)
		}
	return returnObj

@app.post("/pay-loan/{bankUser_id}/{loan_id}", status_code=200)
async def pay_loan(bankUser_id: int, loan_id: int):
	queryBankUserId = 'SELECT Id FROM BankUserId WHERE Id = ?'
	bankuserId = db.execute(queryBankUserId, [bankUser_id]).fetchone()
	if bankUser_id == None:
		raise HTTPException(status_code=404, detail="BankUser Id not found")

	query = """SELECT Loan.Amount AS LoanAmount, Account.Amount AS AccAmount
				FROM Loan 
				INNER JOIN Account
				ON Loan.BankUserId = Account.BankUserId
				WHERE Loan.BankUserId = ? AND Loan.Id = ?;"""
	loanValues = db.execute(query, [bankUser_id, loan_id]).fetchone()
	if loanValues == None:
		raise HTTPException(status_code=404, detail="Loan not found; Could be incorrect BankUser_Id or Loan Id")

	loanAmount = loanValues[0]
	accAmount = loanValues[1]
	
	if loanAmount > accAmount:
		raise HTTPException(status_code=422, detail="Loan greater than account amount")
	else:
		accAmount -= loanAmount
		query2 = """UPDATE Loan
					SET Amount = 0
					WHERE BankUserId = ? AND Id = ?;"""
		db.execute(query2, [bankUser_id, loan_id])

		query3 = """UPDATE Account
					SET Amount = ?
					WHERE BankUserId = ?;"""
		queryAcc = db.execute(query3, [accAmount, bankUser_id])

		db.commit()

	returnObj = {
		'BankUserId': bankUser_id,
		'PaidAmount': loanAmount,
		'CurrentBalance': accAmount
		}
	return returnObj

@app.get("/list-loans/{bankUser_id}", status_code=200)
async def list_loans(bankUser_id: int):
	# Check that user exists
	queryBankUserId = 'SELECT Id FROM BankUserId WHERE Id = ?'
	bankuserId = db.execute(queryBankUserId, [bankUser_id]).fetchone()
	if bankUser_id == None:
		raise HTTPException(status_code=404, detail="BankUser Id not found")

	#Read all loans
	query = 'SELECT * FROM Loan WHERE BankUserId = ?'
	select = db.execute(query, [bankUser_id])

	loans = []
	for row in select:
		loans.append({'Id':row[0], 'BankUserId':row[1], 'CreatedAt':row[2], 'ModifiedAt':row[3], 'Amount':row[4]})

	return loans

## The body of that request should contain an amount and a UserId(Not BankUserId, not SkatUserId)
## Subtract (if possible) the amount from that users account. Throw an error otherwise.
@app.post("/withdrawal-money", status_code=200)
async def withdraw_money(withdrawModel: Withdraw):
	withdrawAmount = float(withdrawModel.Amount)
	bankUserId = int(withdrawModel.BankUserId)

	query = """SELECT Amount FROM Account WHERE BankUserId = ?"""
	selectAccountAmount = db.execute(query, [bankUserId]).fetchone()

	if selectAccountAmount == None:
		raise HTTPException(status_code=404, detail="Account with BankUserId not found")
	elif (withdrawAmount > selectAccountAmount[0]):
		raise HTTPException(status_code=422, detail="withdraw amount is greater than account amount")
	elif (withdrawAmount <= 0):
		raise HTTPException(status_code=422, detail="withdraw amount needs to be greater than 0")
	else:
		query2 = 'UPDATE Account SET amount = ? WHERE BankUserId = ?'
		db.execute(query2, [selectAccountAmount[0] - withdrawAmount, bankUserId])
		db.commit()
	
	returnObj = {
		'BankUserId': bankUserId,
		'WidthdrawAmount': withdrawAmount,
		'CurrentBalance': (selectAccountAmount[0] - withdrawAmount)
	}
	return returnObj

#Start server with uvicorn
if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=5003, log_level="info")