def section_title(title: str):
  print("########################################################")
  print(f"# {title.upper()}")
  print("########################################################")

def subsection_title(subtitle: str):
  print(f"++ {subtitle.upper()}")

def content(content: str | dict):
  print(f"{content}")