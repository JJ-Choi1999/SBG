from fastapi import FastAPI
from api.routers.llm_router import router as llm_router

app = FastAPI(
    title="Fast AI Agent 接口映射",
    description="快速实现AI Agent 功能",
    version="0.0.1"
)

app.include_router(llm_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)