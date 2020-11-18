import requests
import json
from datetime import datetime

#This file contains 3 class to test the different endpoints

baseurl = "http://localhost:5000/api"

#Test Bank API
class bank_test:
    url = baseurl + "/bank"

    #Create user with bankuserid
    def create_user(self, buid, amount):
        print("Creating User")
        obj = {
            "bankUser": {
                "UserId": buid
            },
            "account": {
                "AccountNo": 0,
                "IsStudent": 0,
                "InterestRate": 0,
                "Amount": amount
            }
        }
        response = requests.post(self.url + "/bankUser/create", data=json.dumps(obj))
        print(response.text)

    #Deposit amount into created user
    def deposit(self, buid, amount):
        print("Depositing amount")
        obj = {
            'BankUserId': buid,
            'Amount': amount
        }
        response = requests.post(self.url + "/add-deposit", data=json.dumps(obj))
        print(response.text)

    #Create a new loan into created user
    def create_loan(self, buid, amount):
        print("Creating loan")
        obj = {
            'BankUserId': buid,
            'Amount': amount
        }
        response = requests.post(self.url + "/create-loan", data=json.dumps(obj))
        print(response.text)

    #Pay created loan
    def pay_loan(self, buid):
        print("Paying loan")
        response = requests.post(self.url + "/pay-loan/" + str(buid))
        print(response.text)

#Test Skat API
class skat_test:
    url = baseurl + "/skat"
    
    #create a skat user
    def create_skat_user(self, UserId):
        print("creating a SkatUser")
        obj = {
            "UserId": UserId
        }
        response = requests.post(self.url + "/SkatUser/create", data=json.dumps(obj))
        print(response.text)

    #show a list of skat user
    def show_list_of_SkatUser(self):
        print("Here is a list of SkatUser")
        response = requests.get(self.url + "/SkatUser/readall")
        print(response.text)

    #Create new skat year and all respective skatuseryears
    def skat_year(self, label, startDate, endDate):
        print("Creating SkatYear & SkatUserYears")
        obj = {
            "label": label,
            "startDate": startDate,
            "endDate": endDate
        }
        response = requests.post(self.url + "/SkatYear/create", data=json.dumps(obj, default=str))
        print(response.text)

    def pay_taxes(self, uid, amount):
        print("Paying taxes :(")
        obj = {
            "UserId": uid,
            "Amount": amount
        }
        response = requests.post(self.url + "/pay-taxes", data=json.dumps(obj))
        print(response.text)
   

#Test bank application
print("********************* STARTING SKAT TEST***********************")
bank = bank_test()

buid = 0
accountAmount = 500
depositAmount = 100
loanAmount = 200

bank.create_user(buid, accountAmount)
bank.deposit(buid, depositAmount)
bank.create_loan(buid, loanAmount)
bank.pay_loan(buid)

#Test borger application

#Test skat application
print("********************* STARTING SKAT TEST***********************")
skat = skat_test()

UserId1 = 1
UserId2 = 2
UserId3 = 3

skat.create_skat_user(UserId1)
skat.create_skat_user(UserId2)
skat.create_skat_user(UserId3)

skat.show_list_of_SkatUser()

yearLabel = "2020"
yearStartDate = datetime.fromisoformat('2020-01-01')
yearEndDate = datetime.fromisoformat('2020-12-31')

skat.skat_year(yearLabel, yearStartDate, yearEndDate)
skat.pay_taxes(UserId1, 800)