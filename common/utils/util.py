import datetime
import random
import string


def generate_timestamp():
  return datetime.datetime.now().strftime("%Y%m%d-%H%M%S%f")[:-4]


def generate_random_code():
  """生成随机字符串"""
  characters = string.digits + string.ascii_letters
  code = "".join(random.choice(characters) for _ in range(6))
  return code


def is_qq(msg: str):
  return msg.isdigit() and 11 >= len(msg) >= 5
