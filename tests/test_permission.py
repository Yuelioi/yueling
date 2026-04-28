"""测试权限系统"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


@pytest.fixture
def perm_manager(tmp_path):
  with patch("core.permission.config") as mock_config, \
       patch("core.permission._get_driver_config") as mock_dc:
    mock_config.paths.database = tmp_path
    mock_dc.return_value = MagicMock(superusers=set())

    from core.permission import PermissionManager
    manager = PermissionManager()
    yield manager, mock_dc


def test_permission_level_ordering():
  from core.permission import PermissionLevel
  assert PermissionLevel.BLOCKED < PermissionLevel.MEMBER
  assert PermissionLevel.MEMBER < PermissionLevel.ADMIN
  assert PermissionLevel.ADMIN < PermissionLevel.OWNER
  assert PermissionLevel.OWNER < PermissionLevel.SUPERUSER


def test_get_level_superuser(perm_manager):
  manager, mock_dc = perm_manager
  mock_dc.return_value = MagicMock(superusers={"100001"})
  from core.permission import PermissionLevel
  level = manager.get_level(100001, "member")
  assert level == PermissionLevel.SUPERUSER


def test_get_level_admin(perm_manager):
  manager, mock_dc = perm_manager
  mock_dc.return_value = MagicMock(superusers=set())
  from core.permission import PermissionLevel
  assert manager.get_level(200001, "admin") == PermissionLevel.ADMIN
  assert manager.get_level(200001, "owner") == PermissionLevel.OWNER
  assert manager.get_level(200001, "member") == PermissionLevel.MEMBER


def test_plugin_enable_disable(perm_manager):
  manager, _ = perm_manager
  assert manager.is_plugin_enabled("funny", 12345) is True

  manager.disable_plugin("funny", 12345)
  assert manager.is_plugin_enabled("funny", 12345) is False

  manager.enable_plugin("funny", 12345)
  assert manager.is_plugin_enabled("funny", 12345) is True


def test_user_block_unblock(perm_manager):
  manager, _ = perm_manager
  assert manager.is_user_blocked("roll", 100001) is False

  manager.block_user_plugin("roll", 100001)
  assert manager.is_user_blocked("roll", 100001) is True

  manager.unblock_user_plugin("roll", 100001)
  assert manager.is_user_blocked("roll", 100001) is False
