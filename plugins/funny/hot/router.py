from fastapi import APIRouter

from common.biz import result
from plugins.funny.hot.utils import baidu, bilibili, weibo, zhihu

hot = APIRouter()


@hot.get("/hot")
async def get_hot_messages(type: str = ""):
  if type == "bilibili":
    hot_messages = await bilibili()
  elif type == "zhihu":
    hot_messages = await zhihu()
  elif type == "weibo":
    hot_messages = await weibo()
  elif type == "baidu":
    hot_messages = await baidu()
  else:
    return result.fail("无效的类型，请选择：bilibili, zhihu, weibo, baidu")
  return result.success({"datas": hot_messages})
