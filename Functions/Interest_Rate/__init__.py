import azure.functions as func
import json

#Interest Rate Function
def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        amount = req_body.get('amount')
        interest_rate = req_body.get('interest_rate')

        amount_plus_interest = float(amount) * (1+interest_rate)
        return func.HttpResponse(status_code=200, body=json.dumps({"interest": amount_plus_interest}))