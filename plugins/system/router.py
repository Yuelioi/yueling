from fastapi import APIRouter

from plugins.system.help.router import help

system_router = APIRouter()


# 将子路由添加到父级路由
system_router.include_router(help, prefix="/system", tags=["system"])
