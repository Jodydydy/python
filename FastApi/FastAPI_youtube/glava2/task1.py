from fastapi import FastAPI, HTTPException
from fastapi.responses import Response


app = FastAPI()

BALANCE = {}

@app.get('/balance')
def get_balance(wallet_name: str | None = None):

    if wallet_name is None:
        return {"total_balance": sum(BALANCE.values())}

    if wallet_name not in BALANCE:
        raise HTTPException(
            status_code=404,
            detail=f'Wallet {wallet_name} not found'
        )

    return {'wallet': wallet_name, 'balance': BALANCE[wallet_name]}