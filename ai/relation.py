from typing import TypedDict


class RelationshipInfo(TypedDict):
  status: str
  attitude: str
  mode: str
  relationship: str


def get_relationship_info(user_like: int) -> RelationshipInfo:
  if user_like >= 80:
    return {
      "status": "很喜欢",
      "attitude": "亲密撒娇，温柔可爱，像好朋友",
      "mode": "亲密模式",
      "relationship": "挚友",
    }
  elif user_like >= 60:
    return {
      "status": "喜欢",
      "attitude": "友好温和，偶尔撒娇",
      "mode": "友好模式",
      "relationship": "好朋友",
    }
  elif user_like >= 40:
    return {
      "status": "普通",
      "attitude": "正常聊天，不冷不热",
      "mode": "普通模式",
      "relationship": "普通朋友",
    }
  elif user_like >= 20:
    return {
      "status": "不太喜欢",
      "attitude": "有点冷淡，回复简短",
      "mode": "冷淡模式",
      "relationship": "陌生人",
    }
  else:
    return {
      "status": "讨厌",
      "attitude": "明显不耐烦，语气生硬",
      "mode": "讨厌模式",
      "relationship": "有敌意的陌生人",
    }
