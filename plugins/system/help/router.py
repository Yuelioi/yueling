from fastapi import APIRouter

from common.biz import result
from plugins.system.plugin.manager import hm

help = APIRouter()


@help.get("/help")
async def get_help():
  if hm.commands:
    return result.success(hm.commands)
  return result.fail("初始化失败")
