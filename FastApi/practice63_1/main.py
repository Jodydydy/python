from fastapi import FastAPI
from fastapi_babel import Babel, BabelConfigs, BabelMiddleware, _

app = FastAPI()

babel_configs = BabelConfigs(
    ROOT_DIR=__file__,
    BABEL_DEFAULT_LOCALE="en",
    BABEL_TRANSLATION_DIRECTORY="locales"
)

babel = Babel(configs=babel_configs)

app.add_middleware(BabelMiddleware, babel_configs=babel_configs)

@app.get("/")
async def root():

    return {"message": _("Hello world")}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)