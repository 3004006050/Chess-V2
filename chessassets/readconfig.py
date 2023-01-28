import json
def read_config():
  file = open("chessassets\config.json")
  text = file.read()
  return json.loads(text)
