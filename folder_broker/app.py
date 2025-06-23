from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from rpc_client_async import AsyncRpcClient  # UPDATED import
import os
import logging
import asyncio

LOGGING_ENABLED = os.getenv("LOGGING", "0") == "1"
logging.basicConfig(level=logging.INFO if LOGGING_ENABLED else logging.CRITICAL)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

# Declare global async RPC client
rpc_client: AsyncRpcClient = None

@app.on_event("startup")
async def startup_event():
    global rpc_client
    rpc_client = AsyncRpcClient()
    await rpc_client.connect()
    logging.info("Async RPC client connected")

@app.get("/")
async def read_root(request: Request):
    return templates.TemplateResponse("index2.html", {"request": request})

@app.get("/predict")
async def predict(wine_id: int = Query(...), real_time_measurement: float = Query(...)):
    try:
        payload = {"wine_id": wine_id, "real_time_measurement": real_time_measurement}
        response = await rpc_client.call(payload)
        logging.info("Prediction result: %s", response)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["error"])
        return {"prediction": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# from fastapi import FastAPI, Request, Query, HTTPException
# from fastapi.responses import HTMLResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# from folder_broker.rpc_client import RPCClient
# from dotenv import load_dotenv
# import os
 
# # Load .env file
# load_dotenv(dotenv_path="../.env")

# templates = Jinja2Templates(directory="templates")

# # Define lifespan context
# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     amqp_url = (
#         "amqp://guest:guest@rabbitmq:5672/"
#         if os.getenv("OP_MODE") == "DOCKER"
#         else "amqp://guest:guest@localhost:5672/"
#     )
#     try:
#         app.state.rpc = RPCClient(amqp_url=amqp_url)
#         print("✅ RPCClient connected.")
#     except Exception as e:
#         print(f"❌ Failed to connect to RabbitMQ: {e}")
#         app.state.rpc = None
#     yield
#     if app.state.rpc:
#         app.state.rpc.conn.close()  # optional cleanup
#         print("🧹 RPCClient connection closed.")

# # Create FastAPI app with lifespan
# app = FastAPI(lifespan=lifespan)
 
# # Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # for dev only
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# @app.get("/", response_class=HTMLResponse)
# async def read_root(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.get("/predict", response_class=HTMLResponse)
# async def predict(request: Request, wine_id: int = Query(...), real_time_measurement: float = Query(...)):
#     rpc = request.app.state.rpc
#     if rpc is None:
#         raise HTTPException(status_code=500, detail="RPC client not initialized.")

#     payload = {"wine_id": wine_id, "real_time_measurement": real_time_measurement}
#     try:
#         response = rpc.call(payload, timeout=15)
#         prediction = response.get("prediction")
#         return templates.TemplateResponse("index.html", {"request": request, "prediction": prediction})
#     except TimeoutError as e:
#         raise HTTPException(status_code=504, detail=str(e))
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


