"""NoneBot 依赖注入工具集"""

from core.deps.args import Args, Arg, get_command_args
from core.deps.mentions import At, Ats, get_at_users
from core.deps.media import Img, Imgs, get_imgs

__all__ = [
  "Args", "Arg", "get_command_args",
  "At", "Ats", "get_at_users",
  "Img", "Imgs", "get_imgs",
]
