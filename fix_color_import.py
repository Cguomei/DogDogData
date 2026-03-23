"""
修复 charts.py 中的 opts.Color 调用
在 pyecharts 2.x 中，Color 类已被移除，直接使用颜色字符串即可
"""
import re

# 读取文件
with open('charts.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 使用正则表达式替换 opts.Color("...") 为 "..."
# 匹配 opts.Color("xxx") 并替换为 "xxx"
pattern = r'opts\.Color\("([^"]+)"\)'
replacement = r'"\1"'

content = re.sub(pattern, replacement, content)

# 写回文件
with open('charts.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ 已成功移除所有 opts.Color 包装器")
print("✓ 颜色值已直接嵌入")
