import json

def read_config():

  with open(r"D:\\Chess\\chessassets\\config.json", "r") as param_files:
    text = json.load(param_files)

    return text


