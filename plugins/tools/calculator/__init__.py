import ast
import operator

from nonebot import on_command
from nonebot.plugin import PluginMetadata

from core.deps import Args
from core.handler import register_handler
from core.context import ToolContext

__plugin_meta__ = PluginMetadata(
  name="计算器",
  description="安全数学表达式计算",
  usage="""计算 + 表达式\n如: 计算 12*21""",
  extra={
    "group": "工具",
    "commands": ["计算"],
    "tools": [{
      "name": "calculate",
      "description": "计算数学表达式",
      "tags": ["math"],
      "examples": ["计算 2+3*4", "算一下 100/7", "2的10次方"],
      "parameters": {
        "expression": {"type": "string", "description": "数学表达式"},
      },
      "handler": "calc_tool_handler",
    }],
  },
)

calculator = on_command("计算")

_OPS = {
  ast.Add: operator.add,
  ast.Sub: operator.sub,
  ast.Mult: operator.mul,
  ast.Div: operator.truediv,
  ast.FloorDiv: operator.floordiv,
  ast.Mod: operator.mod,
  ast.Pow: operator.pow,
  ast.BitAnd: operator.and_,
  ast.BitOr: operator.or_,
  ast.BitXor: operator.xor,
  ast.LShift: operator.lshift,
  ast.RShift: operator.rshift,
  ast.USub: operator.neg,
  ast.UAdd: operator.pos,
  ast.Invert: operator.invert,
}

_CMP = {
  ast.Eq: operator.eq,
  ast.NotEq: operator.ne,
  ast.Lt: operator.lt,
  ast.LtE: operator.le,
  ast.Gt: operator.gt,
  ast.GtE: operator.ge,
}


def _safe_eval(node):
  if isinstance(node, ast.Expression):
    return _safe_eval(node.body)
  elif isinstance(node, ast.Constant):
    if not isinstance(node.value, (int, float)):
      raise ValueError("只支持数字")
    return node.value
  elif isinstance(node, ast.BinOp):
    left = _safe_eval(node.left)
    right = _safe_eval(node.right)
    if isinstance(node.op, ast.Pow) and abs(right) > 1000:
      raise ValueError("指数过大")
    op = _OPS.get(type(node.op))
    if not op:
      raise ValueError(f"不支持的运算: {type(node.op).__name__}")
    return op(left, right)
  elif isinstance(node, ast.UnaryOp):
    op = _OPS.get(type(node.op))
    if not op:
      raise ValueError(f"不支持的运算: {type(node.op).__name__}")
    return op(_safe_eval(node.operand))
  elif isinstance(node, ast.Compare):
    left = _safe_eval(node.left)
    for op, comparator in zip(node.ops, node.comparators):
      cmp_fn = _CMP.get(type(op))
      if not cmp_fn:
        raise ValueError(f"不支持的比较: {type(op).__name__}")
      right = _safe_eval(comparator)
      if not cmp_fn(left, right):
        return False
      left = right
    return True
  else:
    raise ValueError("不支持的表达式")


def safe_calculate(expression: str) -> str:
  try:
    tree = ast.parse(expression.strip(), mode="eval")
    result = _safe_eval(tree)
    return str(result)
  except (SyntaxError, ValueError) as e:
    return f"计算错误: {e}"
  except ZeroDivisionError:
    return "除零错误"
  except Exception as e:
    return f"错误: {e}"


async def _calc(args: list[str] = Args()):
  exp = "".join(args).strip()
  if not exp:
    return "请输入表达式"
  return safe_calculate(exp)


register_handler(calculator, _calc)


async def calc_tool_handler(ctx: ToolContext, expression: str) -> str:
  return safe_calculate(expression)
