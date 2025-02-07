def success(data, message: str = "success"):
  return {"code": 200, "msg": message, "data": data}


def fail(data):
  return {"code": -400, "msg": "fail", "data": data}
