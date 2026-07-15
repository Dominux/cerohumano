from fastapi import FastAPI

from app.routers import cerohumano_router, attachment_router


app = FastAPI(prefix='/api/v1')
app.include_router(cerohumano_router)
app.include_router(attachment_router)
