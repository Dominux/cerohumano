from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.routers import cerohumano_router, attachment_router, post_router
from app.common.openapi import custom_openapi


app = FastAPI()
app.openapi = custom_openapi(app)

app.include_router(post_router)
app.include_router(cerohumano_router)
app.include_router(attachment_router)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # This will print the exact field, payload error, or missing multipart boundary in your terminal logs
    print("VALIDATION ERROR LOG:", exc.errors())
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.errors()},
    )
