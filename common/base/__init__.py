"""
存放和机器人基础依赖。

模块说明：
- Depends: 提供依赖注入的功能。
- Ruler: 包含权限检查的工具函数。


使用示例：
1. 使用 Arg 和 Args 来处理命令行参数。
2. 使用 At 和 Ats 来处理用户提及。
3. 使用 Number 和 Numbers 来处理数字相关的操作。
4. 使用 UserImg 和 UserImgs 来处理用户的图片信息。


"""

from common.base.Depends import Arg, Args, At, Ats, Img, Imgs
from common.base.Plugin import load_mods

__all__ = ["Arg", "Args", "At", "Ats", "Img", "Imgs", "load_mods"]
