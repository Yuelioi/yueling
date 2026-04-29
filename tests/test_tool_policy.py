"""验证 tool_policy.resolve_alias"""

from core.tool_policy import TOOL_POLICY, resolve_alias


def test_resolve_alias_empty_policy():
  assert resolve_alias("translate", {"translate_v2"}) is None


def test_resolve_alias_returns_first_available():
  TOOL_POLICY["translate"] = ["translate_v2", "translate_basic"]
  try:
    assert resolve_alias("translate", {"translate_basic", "translate_v2"}) == "translate_v2"
    assert resolve_alias("translate", {"translate_basic"}) == "translate_basic"
  finally:
    del TOOL_POLICY["translate"]


def test_resolve_alias_all_unavailable():
  TOOL_POLICY["translate"] = ["translate_v2", "translate_basic"]
  try:
    assert resolve_alias("translate", {"other_tool"}) is None
  finally:
    del TOOL_POLICY["translate"]
