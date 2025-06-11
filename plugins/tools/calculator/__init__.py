import ast

from nonebot import on_command
from nonebot.plugin import PluginMetadata

from common.base.Depends import Args
from common.base.Handle import register_handler

__plugin_meta__ = PluginMetadata(
  name="计算器",
  description="加减乘除/比较/位运算/幂模/大于小于",
  usage="""计算 + 需要计算的内容
如计算 12*21
  """,
  extra={"group": "工具", "commands": ["计算"]},
)

calculator = on_command("计算")


async def _calc(args: list[str] = Args()):
  exp = "".join(args).strip()
  allow = [
    ast.Module,  # 根节点
    ast.Expr,  # 表达式
    ast.Constant,  # 常量
    ast.BinOp,
    ast.Add,
    ast.Sub,
    ast.Mult,
    ast.Div,
    ast.FloorDiv,  # 整数除法
    ast.Mod,  # 取模
    ast.Pow,  # 幂运算
    ast.BitAnd,  # 位与
    ast.BitOr,  # 位或
    ast.BitXor,  # 位异或
    ast.LShift,  # 位左移
    ast.RShift,  # 位右移
    ast.Invert,  # 位取反
    ast.UAdd,  # 正号
    ast.USub,  # 负号
    ast.Compare,  # 比较操作符
    ast.Eq,  # 等于
    ast.NotEq,  # 不等于
    ast.Lt,  # 小于
    ast.LtE,  # 小于等于
    ast.Gt,  # 大于
    ast.GtE,  # 大于等于
  ]

  try:
    tree = ast.parse(exp)
  except SyntaxError:
    return "语法错误"

  all_allowed = all(any(isinstance(node, rule) for rule in allow) for node in ast.walk(tree))
  if all_allowed:
    code_obj = compile(exp, "<string>", "eval")
    try:
      result = eval(code_obj)
      return str(result)
    except Exception as e:
      return str(e)

  else:
    return "语法错误"


register_handler(calculator, _calc)
