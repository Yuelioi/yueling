from fastapi import APIRouter, File, UploadFile

trace_moe = APIRouter()
from common.biz import result
from plugins.funny.trace_moe.utils import trace_character_util, trace_moe_util


@trace_moe.post("/trace-moe", response_model=dict)
async def trace_moe_handler(file: UploadFile = File(...)):
  file_bytes = await file.read()
  res = await trace_moe_util(file_bytes)
  if res:
    return result.success({"datas": res})
  return result.fail("获取失败")


@trace_moe.post("/trace-character", response_model=dict)
async def trace_character_handler(file: UploadFile = File(...)):
  if not file.content_type or not file.content_type.startswith("image/"):
    return result.fail("文件类型错误，必须是图片格式的文件")
  file_bytes = await file.read()

  if not file_bytes:
    return result.fail("文件内容为空")

  res = await trace_character_util(file_bytes, file.filename or "test.jpg")
  if res:
    return result.success({"datas": res})

  return result.fail("获取失败")
