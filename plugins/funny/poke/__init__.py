import random
import time

from nonebot import on_notice
from nonebot.adapters.onebot.v11 import Bot, PokeNotifyEvent
from nonebot_plugin_alconna import MsgTarget

from common.Alc.Alc import pm, register_handler
from common.utils import get_random_image

__plugin_meta__ = pm(
  name="戳一戳",
  description="戳一戳月灵反馈",
  usage="""戳一戳月灵""",
  group="娱乐",
)


user_data = {}

pk = on_notice()


async def poke_detect(bot: Bot, target: MsgTarget, event: PokeNotifyEvent):
  """戳一戳事件监听"""

  if target.private:
    return random.choice(
      [
        "戳什么戳?",
        "别戳啦!!",
      ]
    )
  group_id = event.group_id if event.group_id else 0
  if str(event.target_id) == bot.self_id:
    bot_info = await bot.get_group_member_info(group_id=group_id, user_id=int(bot.self_id))
    target_info = await bot.get_group_member_info(group_id=group_id, user_id=event.user_id)

    if bot_info.get("role") == "admin" and target_info.get("role") == "member":
      current_timestamp = time.time()
      if current_timestamp < user_data.get(event.user_id, 0):
        return
      else:
        words = [
          "气运之子!恭喜你获得SSR级禁言卡「{}」分钟",
          "扶额,别戳啦! SR级禁言卡「{}」分钟",
          "闹够了没有! 奖励R级禁闭「{}」分钟",
          "敢乱戳本小姐, 奖励N级禁言卡「{}」分钟",
        ]

        options = [1, 500, 1500, 3000]
        weights = [5, 15, 30, 50]

        random_number = random.choices(options, weights)[0]
        idx = options.index(random_number)

        if idx != 0:
          rnd_out = random.randint(options[idx - 1], random_number)
        else:
          rnd_out = random.randint(0, random_number)

        user_data[event.user_id] = current_timestamp + 60 * rnd_out
        await bot.set_group_ban(group_id=group_id, user_id=event.user_id, duration=rnd_out * 60)
        return words[idx].format(rnd_out)
    else:
      nickname = target_info.get("nickname", "")
      return f"姓{nickname[0]}的,你戳什么戳!"

  img_folder = "拍一拍"
  if matching_file := get_random_image(img_folder, str(event.target_id)):
    return matching_file


register_handler(pk, poke_detect)
