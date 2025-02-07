from fastapi import APIRouter

router = APIRouter()

from plugins.funny.router import funny_router
from plugins.group.router import group_router
from plugins.system.router import system_router

router.include_router(funny_router)
router.include_router(group_router)
router.include_router(system_router)
