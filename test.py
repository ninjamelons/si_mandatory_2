import requests
import json

baseurl = "http://localhost:5000/api"

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
    def deposit(self, buid, amount):
        print("Depositing amount")
        obj = {
            'BankUserId': buid,
            'Amount': amount
        }
        response = requests.post(self.url + "/add-deposit", data=json.dumps(obj))
        print(response.text)
    def create_loan(self, buid, amount):
        print("Creating loan")
        obj = {
            'BankUserId': buid,
            'Amount': amount
        }
        response = requests.post(self.url + "/create-loan", data=json.dumps(obj))
        print(response.text)
    def pay_loan(self, buid):
        print("Paying loan")
        response = requests.post(self.url + "/pay-loan/" + str(buid))
        print(response.text)

#Test banking application
bank = bank_test()

buid = 0
accountAmount = 500
depositAmount = 100
loanAmount = 200

bank.create_user(buid, accountAmount)
bank.deposit(buid, depositAmount)
bank.create_loan(buid, loanAmount)
bank.pay_loan(buid)