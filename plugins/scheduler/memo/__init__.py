import re
from datetime import datetime, timedelta

from nonebot import get_bot
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment
from nonebot_plugin_alconna import Alconna, Args, At, on_alconna
from nonebot_plugin_apscheduler import scheduler

from common.Alc.Alc import pm, ptc

__plugin_meta__ = pm(
  name="定时提醒",
  description="提醒做什么事情",
  usage="""提醒@用户 x小时x分钟x秒后内容""",
  group="定时任务",
)

_memo = Alconna("提醒", Args["user", At]["content", str])

_memo.meta = ptc(__plugin_meta__)
memo = on_alconna(_memo)


@memo.handle()
async def setu_h(event: GroupMessageEvent, user: At, content: str):
  origin = event.get_plaintext()
  if "提醒" not in origin:
    return

  task_delay, task_content = extract_time_and_content(event.get_plaintext())

  task_content = task_content.replace("我", "")

  if len(task_content) == 0:
    return
  task_content = "该" + task_content + "啦"
  userId = user.target
  if userId == 435826135:
    task_content = "爹地, " + task_content + "~"

  taskId = f"qq-{event.group_id}-{userId}-{datetime.now().timestamp()}"
  msg = MessageSegment.at(user.target) + MessageSegment.text(task_content)

  job = scheduler.add_job(
    func=reminder,
    name=taskId,
    id=taskId,
    trigger="date",
    next_run_time=datetime.now() + timedelta(seconds=task_delay),
    args=[
      event.group_id,
      event.user_id,
      msg,
    ],
  )
  print(job.id)
  scheduler.remove_job(job.id)


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
