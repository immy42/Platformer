import json

with open(r"data\to_import.json") as json_file:
    print("opened")
    b = json.load(json_file)
json_file.close()
print(b)
print(b["platforms"][0][0])