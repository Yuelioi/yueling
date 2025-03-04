import re
from datetime import datetime, timedelta

from apscheduler.job import Job
from nonebot import get_bot, on_keyword
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot.plugin import PluginMetadata
from nonebot_plugin_apscheduler import scheduler

from common.base.Depends import At

__plugin_meta__ = PluginMetadata(
  name="定时提醒",
  description="提醒做什么事情",
  usage="""提醒@用户 x小时x分钟x秒后内容""",
  extra={"group": "定时任务"},
)


memo = on_keyword(keywords={"提醒"})


# TODO 查看提醒
@memo.handle()
async def setu_h(event: GroupMessageEvent, user=At(False)):
  origin = event.get_plaintext()

  if "查看提醒" in origin:
    return

  task_delay, task_content = extract_time_and_content(origin)

  task_content = task_content.replace("我", "").replace("提醒", "").strip()

  # 跳过解析失败的
  if not task_content:
    return

  if task_delay < 5:
    return

  task_content = "该" + task_content + "啦"

  if "提醒我" in origin:
    user = event.user_id

  if user == 435826135:
    task_content = "爹地, " + task_content + "~"

  taskId = f"qq-{event.group_id}-{user}-{datetime.now().timestamp()}"
  msg = MessageSegment.at(user) + MessageSegment.text(task_content)

  print(task_content)

  scheduler.add_job(
    func=reminder,
    name=taskId,
    id=taskId,
    trigger="date",
    next_run_time=datetime.now() + timedelta(seconds=task_delay),
    args=[
      event.group_id,
      user,
      msg,
    ],
  )

  jobs: list[Job] = scheduler.get_jobs()

  print(jobs[0].next_run_time)


async def reminder(
  group_id: int,
  user_id: int,
  msg,
):
  bot = get_bot()
  await bot.send_group_msg(group_id=group_id, user_id=user_id, message=msg)


def extract_time_and_content(
  text,
):  # -> list[FixtureFunction[SimpleFixtureFunction, FactoryFixtur...:# -> list[FixtureFunction[SimpleFixtureFunction, FactoryFixtur...:# -> list[FixtureFunction[SimpleFixtureFunction, FactoryFixtur...:# -> list[FixtureFunction[SimpleFixtureFunction, FactoryFixtur...:
  # 匹配时间和内容的正则表达式，支持可选的小时、分钟和秒
  pattern = re.compile(r"((?:(\d+)(小时|h))?(?:(\d+)(分钟|m))?(?:(\d+)(秒|s))?)后(.+?)(?=\d+|$)")
  matches = pattern.findall(text)
  total_seconds = 0
  content = ""
  for match in matches:
    hours = int(match[1]) if match[1] else 0
    minutes = int(match[3]) if match[3] else 0
    seconds = int(match[5]) if match[5] else 0
    content = match[7]

    total_seconds = timedelta(hours=hours, minutes=minutes, seconds=seconds).total_seconds()

  return total_seconds, content.strip()


def extract_user_from_content(content):
  user_pattern = re.compile(r"\d{5,}")
  user_match = user_pattern.search(content)
  if user_match:
    user = int(user_match.group(0))
    # 移除匹配的用户ID部分
    content = user_pattern.sub("", content).strip()
  else:
    user = None
  return user, content
