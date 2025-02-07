from fastapi import APIRouter

from plugins.funny.chat.router import chat
from plugins.funny.hot.router import hot
from plugins.funny.trace_moe.router import trace_moe

funny_router = APIRouter()


# 将子路由添加到父级路由
funny_router.include_router(chat, prefix="/funny", tags=["funny"])
funny_router.include_router(hot, prefix="/funny", tags=["funny"])
funny_router.include_router(trace_moe, prefix="/funny", tags=["funny"])
