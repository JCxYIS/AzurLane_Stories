import re
text = "<size=45>一  火锅大会喵！</size>"
text = re.sub(
    r'<size=(\d+)>(.*?)</size>',
    lambda m: f'<span style="font-size: {int(m.group(1))/60.0:.3f}em;">{m.group(2)}</span>',
    text,
    flags=re.IGNORECASE|re.DOTALL
)
print("RESULT:", text)
