import azure.functions as func

#Loan Algorithm Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        amount = req_body.get('amount')
        loan = req_body.get('loan')
        if loan > (0.75*amount):
            return func.HttpResponse("Loan greater than 75% of account amount", status_code=403)
        else:
            return func.HttpResponse("Loan in check", status_code=200)