def section_title(title: str):
  print("###################################")
  print(f"# {title.capitalize}")
  print("###################################")

def content(subtitle: str, content: str | dict):
  print(f"++ {subtitle}")
  if isinstance(content, dict):
    pretty(content)
  else:
    print(content)

def pretty(d, indent=0):
  for key, value in d.items():
    print('\t' * indent + str(key))
    if isinstance(value, dict):
      pretty(value, indent+1)
    else:
      print('\t' * (indent+1) + str(value))