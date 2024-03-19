class Logger:
  def __init__(self, filepath: str):
    self.filepath = filepath

  def content(self, content: str):
    print(f"{content}", end="")
    with open(self.filepath, "a") as f:
      f.write(content)

def make_logger(filepath: str) -> Logger:
  return Logger(filepath)