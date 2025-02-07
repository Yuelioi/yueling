## 事件响应器

对应nb文档 [事件响应器进阶](https://nonebot.dev/docs/next/advanced/matcher)

`rule` `permission`等 alc与nonebot与区别, 故只专注命令本身以及如何在handle函数里使用

## 响应规则

### startswith

消息纯文本`开头`为指定命令

```python
# nb
on_startswith("!")
on_startswith(("!", "/"))
# alc
test = on_alconna(
  Alconna( ["/", "!"], 
    Args["args?", MultiVar(str, "+")],
  ),
)
```

### endswith

消息纯文本`结尾`为指定命令

```python
# nb
endswith((".", "。"))
# alc
# 注意 \ 需要使用转义, 与普通正则一致
# .*代表匹配任意字符 $表示以前面结尾
on_alconna(Alconna(f"re:.*。$"))
on_alconna(Alconna(f"re:.*[。|\\.]$"))
```

### fullmatch

消息纯文本与指定命令`完全相同`

```python
# nb
on_fullmatch(msg: Union[str, tuple[str, ...]])
on_fullmatch("单个命令")
on_fullmatch(("命令A", "命令B"))

# alc
on_alconna(Alconna("单个命令"))
on_alconna(Alconna("命令A"), aliases={"命令B"})
```

### keyword

消息纯文本`包含`指定命令

```python
# nb
on_keyword({"单个命令"})
on_keyword({"命令A", "命令B"})

# alc
on_alconna(Alconna(f"re:.*单个命令.*"))
on_alconna(Alconna(f"re:.*(命令A|命令B).*"))
```

### command

消息开头为 命令提示符 + 指定命令

```python
# nb
command("help", "帮助")
# alc
# arg 代表必须传且只能传1个参数
# MultiVar 多参数
on_alconna(
  Alconna(
    "help",
    Args["arg", str],
  ),
  aliases={"帮助"},
)

on_alconna(
  Alconna(
    "help",
    Args["args", MultiVar(str, "*")],
  ),
  aliases={"帮助"},
)
```

### shell_command

```python
# nb
parser = ArgumentParser()
parser.add_argument("-v", "--verbose", action="store_true")
rule = shell_command("cmd", parser=parser)

# alc
```

### regex

```python
# nb
regex(r"[a-z]+", flags=re.IGNORECASE)

# alc`
# 正常写正则即可
on_alconna(Alconna(f"re:[a-z]+"))
```

### to_me

```python
# nb

# alc
```

## 响应器组

### CommandGroup

```python
# nb

# alc
```

### MatcherGroup

```python
# nb

# alc
```
