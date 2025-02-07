from fastapi import APIRouter

from plugins.group.file.router import file

group_router = APIRouter()


group_router.include_router(file, prefix="/group", tags=["group"])
