import uvicorn
import asyncio
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
# from fastapi_jsonrpc import API, JsonRpcRouter
from src.auth.auth_router import router as auth_router
from src.routers.users_router import router as users_router
from src.routers.headsets_router import router as headset_router
from src.routers.bookings_router import router as booking_router
from src.routers.email_router import router as email_router
from src.routers.admin_router import router as admin_router

from config.config import CORS_ORIGINS
from config.init_db import init_db


app = FastAPI(
    title="vr_reservation",
    root_path="/api"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"]
)
app.include_router(
    users_router,
    prefix="/users",
    tags=["Users"]
)
app.include_router(
    headset_router,
    prefix="/bookings",
    tags=["Bookings"]
)
app.include_router(
    admin_router,
    prefix="/bookings",
    tags=["Admin"]
)
app.include_router(
    booking_router,
    prefix="/bookings",
    tags=["Bookings"]
)
app.include_router(
    email_router,
    prefix="/email",
    tags=["Email"]
)


async def main():
    await init_db()

    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000
    )
    server = uvicorn.Server(config)
    await server.serve()
    

if __name__ == "__main__":
    asyncio.run(main())
