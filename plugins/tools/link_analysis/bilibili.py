import json
import re
import urllib.parse
from time import localtime, strftime

import aiohttp
import nonebot
from nonebot.adapters.onebot.v11 import Message, MessageSegment

from common.utils import text_to_image

analysis_stat: dict[int, str] = {}

config = nonebot.get_driver().config
analysis_display_image = getattr(config, "analysis_display_image", True)
analysis_display_image_list = getattr(config, "analysis_display_image_list", [])


async def bilibili(url):
  if msg := await bili_keyword(url):
    return msg


async def fetch_json(url):
  headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
  async with aiohttp.request("GET", url, headers=headers, timeout=aiohttp.client.ClientTimeout(10)) as resp:
    return await resp.json()


async def bili_keyword(text: str):
  try:
    # 提取url
    url, page, time_location = extract(text)

    # 如果是小程序就去搜索标题
    if not url:
      if title := re.search(r'"desc":("[^"哔哩]+")', text):
        vurl = await search_bili_by_title(title[1])
        if vurl:
          url, page, time_location = extract(vurl)

    # 获取视频详细信息
    msg, vurl = "", ""
    if "view?" in url:
      msg, vurl = await video_detail(url, page=page, time_location=time_location)
    elif "bangumi" in url:
      msg, vurl = await bangumi_detail(url, time_location)
    elif "xlive" in url:
      msg, vurl = await live_detail(url)
    elif "article" in url:
      msg, vurl = await article_detail(url, page)
    elif "dynamic" in url:
      msg, vurl = await dynamic_detail(url)

  except Exception as e:
    msg = f"bili_keyword Error: {type(e)}"
  return msg


def extract(text: str):
  # 匹配 p 和 t 参数
  p_match = re.search(r"([?&]|&amp;)p=(\d+)", text)
  t_match = re.search(r"([?&]|&amp;)t=(\d+)", text)
  page = p_match[2] if p_match else ""
  time = t_match[2] if t_match else "None"

  # 匹配不同类型的视频链接

  # 根据匹配结果生成 URL
  if aid := re.search(r"av\d+", text, re.I):
    url = f"https://api.bilibili.com/x/web-interface/view?aid={aid[0][2:]}"
  elif bvid := re.search(r"BV([A-Za-z0-9]{10})+", text, re.I):
    url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid[0]}"
  elif epid := re.search(r"ep\d+", text, re.I):
    url = f"https://api.bilibili.com/pgc/view/web/season?ep_id={epid[0][2:]}"
  elif ssid := re.search(r"ss\d+", text, re.I):
    url = f"https://api.bilibili.com/pgc/view/web/season?season_id=={ssid[0][2:]}"
  elif mdid := re.search(r"md\d+", text, re.I):
    url = f"https://api.bilibili.com/pgc/review/user?media_id={mdid[0][2:]}"
  elif room_id := re.search(r"live.bilibili.com/(blanc/|h5/)?(\d+)", text, re.I):
    url = f"https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom?room_id={room_id[2]}"
  elif cvid := re.search(r"(/read/(cv|mobile|native)(/|\?id=)?|^cv)(\d+)", text, re.I):
    page = cvid[4]
    url = f"https://api.bilibili.com/x/article/viewinfo?id={page}&mobi_app=pc&from=web"
  elif dynamic_id_type2 := re.search(r"(t|m).bilibili.com/(\d+)\?(.*?)(&|&amp;)type=2", text, re.I):
    url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?rid={dynamic_id_type2[2]}&type=2"
  elif dynamic_id := re.search(r"(t|m).bilibili.com/(\d+)", text, re.I) or re.search(r"(.+bilibili.com)/opus/(\d+)", text, re.I):
    url = f"https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/get_dynamic_detail?dynamic_id={dynamic_id[2]}"
  else:
    url = ""

  return url, page, time


async def search_bili_by_title(title: str):
  url = f"https://api.bilibili.com/x/web-interface/search/all/v2?keyword={urllib.parse.quote(title)}"

  result = (await fetch_json(url))["data"]["result"]

  for i in result:
    if i.get("result_type") != "video":
      continue
    # 只返回第一个结果
    return i["data"][0].get("arcurl")


# 处理超过一万的数字
def handle_num(num: int) -> str:
  return f"{num / 10000:.2f}万" if num >= 10000 else str(num)


async def video_detail(url: str, **kwargs) -> tuple[Message | str, str]:
  try:
    res = (await fetch_json(url)).get("data", {})
    if not res:
      return "解析到视频被删了/稿件不可见或审核中/权限不足", url
    vurl = f"https://www.bilibili.com/video/av{res['aid']}"

    cover = MessageSegment.image(res["pic"]) if analysis_display_image or "video" in analysis_display_image_list else MessageSegment.text("")
    title = f"标题：{res['title']}"
    pubdate = strftime("%Y-%m-%d %H:%M:%S", localtime(res["pubdate"]))
    tname = f"类型：{res['tname']} | UP：{res['owner']['name']} | 日期：{pubdate}\n"
    stat = f"播放：{handle_num(res['stat']['view'])} | 弹幕：{handle_num(res['stat']['danmaku'])} | 收藏：{handle_num(res['stat']['favorite'])}\n"
    stat += f"点赞：{handle_num(res['stat']['like'])} | 硬币：{handle_num(res['stat']['coin'])} | 评论：{handle_num(res['stat']['reply'])}\n"
    desc = f"简介：{res['desc']}"

    img_path = text_to_image([title, tname, stat, desc])
    img = MessageSegment.image(img_path)

    msg = Message([cover, MessageSegment.text(vurl), img])
    return msg, vurl
  except Exception as e:
    nonebot.logger.error(e)
    msg = f"视频解析出错--Error: {type(e)}"
    return msg, ""


async def bangumi_detail(url: str, time_location: str):
  try:
    res = (await fetch_json(url)).get("result")
    if not res:
      return None, None
    cover = MessageSegment.image(res["cover"]) if analysis_display_image or "bangumi" in analysis_display_image_list else MessageSegment.text("")
    title = f"番剧：{res['title']}\n"
    desc = f"{res['newest_ep']['desc']}\n"
    index_title = ""
    style = "".join(f"{i}," for i in res["style"])
    style = f"类型：{style[:-1]}\n"
    evaluate = f"简介：{res['evaluate']}\n"
    if "season_id" in url:
      vurl = f"https://www.bilibili.com/bangumi/play/ss{res['season_id']}"
    elif "media_id" in url:
      vurl = f"https://www.bilibili.com/bangumi/media/md{res['media_id']}"
    else:
      epid = re.compile(r"ep_id=\d+").search(url)
      if epid:
        epid = epid[0][len("ep_id=") :]
      for i in res["episodes"]:
        if str(i["ep_id"]) == epid:
          index_title = f"标题：{i['index_title']}\n"
          break
      vurl = f"https://www.bilibili.com/bangumi/play/ep{epid}"
    if time_location:
      time_location = time_location[0].replace("&amp;", "&")[3:]
      vurl += f"?t={time_location}"

    img_path = text_to_image([title, index_title, style, evaluate, desc])
    img = MessageSegment.image(img_path)
    msg = Message([cover, MessageSegment.text(f"{vurl}\n"), img])
    return msg, vurl
  except Exception as e:
    msg = f"番剧解析出错--Error: {type(e)}"
    msg += f"\n{url}"
    return msg, None


async def live_detail(url: str):
  try:
    res = await fetch_json(url)
    if res["code"] != 0:
      return None, None
    res = res["data"]
    uname = res["anchor_info"]["base_info"]["uname"]
    room_id = res["room_info"]["room_id"]
    title = res["room_info"]["title"]
    cover = (
      MessageSegment.image(res["room_info"]["cover"]) if analysis_display_image or "live" in analysis_display_image_list else MessageSegment.text("")
    )
    live_status = res["room_info"]["live_status"]
    lock_status = res["room_info"]["lock_status"]
    parent_area_name = res["room_info"]["parent_area_name"]
    area_name = res["room_info"]["area_name"]
    online = res["room_info"]["online"]
    tags = res["room_info"]["tags"]
    watched_show = res["watched_show"]["text_large"]
    vurl = f"https://live.bilibili.com/{room_id}\n"
    if lock_status:
      lock_time = res["room_info"]["lock_time"]
      lock_time = strftime("%Y-%m-%d %H:%M:%S", localtime(lock_time))
      title = f"[已封禁]直播间封禁至：{lock_time}\n"
    elif live_status == 1:
      title = f"[直播中]标题：{title}\n"
    elif live_status == 2:
      title = f"[轮播中]标题：{title}\n"
    else:
      title = f"[未开播]标题：{title}\n"
    up = f"主播：{uname}  当前分区：{parent_area_name}-{area_name}\n"
    watch = f"观看：{watched_show}  直播时的人气上一次刷新值：{handle_num(online)}\n"
    if tags:
      tags = f"标签：{tags}\n"
    if live_status:
      player = f"独立播放器：https://www.bilibili.com/blackboard/live/live-activity-player.html?enterTheRoom=0&cid={room_id}"
    else:
      player = ""

    img_path = text_to_image([title, up, watch, tags, player])
    img = MessageSegment.image(img_path)
    msg = Message([cover, MessageSegment.text(vurl), img])
    return msg, vurl
  except Exception as e:
    msg = f"直播间解析出错--Error: {type(e)}"
    return msg, None


async def article_detail(url: str, cvid: str):
  try:
    res = (await fetch_json(url)).get("data")
    if not res:
      return None, None
    images = [MessageSegment.image(i) for i in res["origin_image_urls"]] if analysis_display_image or "article" in analysis_display_image_list else []
    vurl = f"https://www.bilibili.com/read/cv{cvid}"
    title = f"标题：{res['title']}\n"
    up = f"作者：{res['author_name']} (https://space.bilibili.com/{res['mid']})\n"
    view = f"阅读数：{handle_num(res['stats']['view'])} "
    favorite = f"收藏数：{handle_num(res['stats']['favorite'])} "
    coin = f"硬币数：{handle_num(res['stats']['coin'])}"
    share = f"分享数：{handle_num(res['stats']['share'])} "
    like = f"点赞数：{handle_num(res['stats']['like'])} "
    dislike = f"不喜欢数：{handle_num(res['stats']['dislike'])}"
    desc = view + favorite + coin + "\n" + share + like + dislike + "\n"

    img_path = text_to_image([title, up, view, favorite, like, desc])
    img = MessageSegment.image(img_path)
    msg = Message(images)
    msg.extend([MessageSegment.text(vurl), img])
    return msg, vurl
  except Exception as e:
    msg = f"专栏解析出错--Error: {type(e)}"
    return msg, None


async def dynamic_detail(url: str):
  try:
    res = (await fetch_json(url))["data"].get("card")
    if not res:
      return None, None
    card = json.loads(res["card"])
    dynamic_id = res["desc"]["dynamic_id"]
    vurl = f"https://t.bilibili.com/{dynamic_id}\n"
    if not (item := card.get("item")):
      return "动态不存在文字内容", vurl
    if not (content := item.get("description")):
      content = item.get("content")
    content = content.replace("\r", "\n")
    if len(content) > 250:
      content = f"{content[:250]}......"
    images = item.get("pictures", []) if analysis_display_image or "dynamic" in analysis_display_image_list else []
    if images:
      images = [MessageSegment.image(i.get("img_src")) for i in images]
    elif pics := item.get("pictures_count"):
      content += f"\nPS：动态中包含{pics}张图片"
    if origin := card.get("origin"):
      jorigin = json.loads(origin)
      if short_link := jorigin.get("short_link"):
        content += f"\n动态包含转发视频{short_link}"
      else:
        content += "\n动态包含转发其他动态"
    img_path = text_to_image([content])
    img = MessageSegment.image(img_path)
    msg = Message(img)
    msg.extend(images)
    msg.append(f"\n{vurl}")
    return msg, vurl
  except Exception as e:
    msg = f"动态解析出错--Error: {type(e)}"
    return msg, None
