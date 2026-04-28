"""共享 fixtures — mock bot / event / config"""

import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_bot():
  bot = AsyncMock()
  bot.self_id = "123456"
  bot.adapter = MagicMock()
  bot.adapter.get_name.return_value = "OneBot V11"
  bot.call_api = AsyncMock(return_value={})
  bot.get_group_member_info = AsyncMock(return_value={"role": "member", "nickname": "test_user", "card": ""})
  bot.get_group_member_list = AsyncMock(return_value=[])
  return bot


@pytest.fixture
def mock_event():
  event = MagicMock()
  event.user_id = 100001
  event.group_id = 200001
  event.message_id = "msg_001"
  event.message = []
  event.reply = None
  event.get_plaintext.return_value = "测试消息"
  event.is_tome.return_value = False
  event.sender = MagicMock()
  event.sender.nickname = "test_user"
  return event


@pytest.fixture
def tool_context(mock_bot, mock_event):
  from core.context import ToolContext
  return ToolContext(
    user_id=mock_event.user_id,
    group_id=mock_event.group_id,
    role="member",
    bot=mock_bot,
    event=mock_event,
  )
