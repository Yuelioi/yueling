from core.http import get_client, USER_AGENT


async def bilibili():
  client = get_client()
  response = await client.get(
    "https://app.bilibili.com/x/topic/web/dynamic/rcmd?source=Web&page_size=10",
    headers={"User-Agent": USER_AGENT},
  )
  if response.status_code == 200:
    topic_items = response.json()["data"]["topic_items"]
    res = [item["name"] for item in topic_items]
    return [f"{index + 1}. {d}" for index, d in enumerate(res)]
  return []


async def zhihu():
  client = get_client()
  response = await client.get("https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=50&desktop=true")
  if response.status_code == 200:
    topic_items = response.json()["data"][:10]
    res = [item["target"]["title"] for item in topic_items]
    return [f"{index + 1}. {d}" for index, d in enumerate(res)]
  return []


async def weibo():
  client = get_client()
  response = await client.get("https://weibo.com/ajax/side/hotSearch")
  if response.status_code == 200:
    topic_items = response.json()["data"]["realtime"][:10]
    res = [item["word"] for item in topic_items]
    return [f"{index + 1}. {d}" for index, d in enumerate(res)]
  return []


async def baidu():
  client = get_client()
  response = await client.get("https://top.baidu.com/api/board?platform=wise&tab=realtime")
  if response.status_code == 200:
    topic_items = response.json()["data"]["cards"][0]["content"][:10]
    res = [item["query"] for item in topic_items]
    return [f"{index + 1}. {d}" for index, d in enumerate(res)]
  return []
