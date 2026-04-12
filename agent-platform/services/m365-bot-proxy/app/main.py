import os
from fastapi import FastAPI, Request, Response
from botbuilder.core import BotFrameworkAdapter, BotFrameworkAdapterSettings
from botbuilder.schema import Activity

# This is a proxy service for Microsoft 365 / Teams channel integration.
# It acts as the adapter surface, forwarding activities to the Pulser gateway.

app = FastAPI()

settings = BotFrameworkAdapterSettings(
    os.environ.get("MicrosoftAppId", ""),
    os.environ.get("MicrosoftAppPassword", "")
)
adapter = BotFrameworkAdapter(settings)

@app.get("/health")
async def health():
    return {"status": "ok", "service": "m365-bot-proxy"}

@app.post("/api/messages")
async def messages(request: Request):
    # Main entry point for Teams activity
    if "application/json" not in request.headers.get("content-type", ""):
        return Response(status_code=415)

    try:
        body = await request.json()
        activity = Activity().deserialize(body)
        auth_header = request.headers.get("Authorization", "")

        # Logic to forward to Pulser Copilot Gateway or process locally
        # response = await adapter.process_activity(activity, auth_header, bot.on_turn)
        
        return Response(status_code=200)
    except PermissionError as err:
        return Response(status_code=401, content=str(err))
    except Exception:
        return Response(status_code=500)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
