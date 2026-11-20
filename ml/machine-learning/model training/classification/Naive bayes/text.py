import base64
import re
import requests

image_url = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAJYAAABGCAIAAAChXfqaAAADNUlEQVR4Xu2WQW4UQQxF+wDZs05yAtbZswrb3IGbIIRQDgFcIBILOEC2XCFXgJKyZURJPdX+Lrfb091VnrH1NnGVPZZfapIhpdfANQOmAl+EQveEQveEQveEQveEQveEQveEQveEQveEQveEQveEQveEQveEQveEQveEQveEQveEQvcsUzhUAm8Gu6HdPpU2Dbwf7IZ2+1TaNPB+sBva7VNp02AvY5NgC7SLJlaO9qZ59rQW+CmBAeMeBRnkSAhsq+fn1RdMXiYze7x79/0A5gUZ5KgW2HMRoXDEuErBBzmqBfZcSljMGFcp+KjlVycUZoxbLj0RVbX86oTCjHHLpSeiihyRwFZmQmHGuFNBDDnCwG5mwmJqonBYz2IoTK0UDitZDIVpC4Us5L6mRElYNK7S4MNQoiEUaldJBMiB5WwHvGOAKPxx/4x3zhvtHun6xcBytgPeMRCvULtHun4xsBw74AUzF25Ru0oiQBNyLX6EmVBIU2aoJTGw3EwopCkz1FI9sPZEdrD4cPsBkz2w8japKy6w6nR2UNgtmyw0s6k50jAUNuP66zUmNeBvxsVdKnw+LRDYXOFyWQR/aVQ2JBQeCLtFaa6RVbVmCT5dJrFX39vELzWIXQLTZhVWAojP5awClEMCxZ6gVlEE9Bi4W54ef+x/DEHajgoxCR+1pnRQOHjt7eYLBWiBpZB/RDPG2YLm5K3f7B4AK1ksCpDn2ER450dFD79eYPJhqymEE2wlCXkOeJ3KULVTSMpFNKa/4HXHDE/PWpgwUIN7JdqDbLxQsExLyukBdPA+y5g/ilYxY2e/KWKeaS2a5IULI4daoEl/dPL0LMW9YuuKSw7CIGFndPRxPJz1K9YqbCWL49c0N24NYuL9staLBzRPsJR//Q4Lmtx0X5DYXvkL9VZWIWp8ge1TJIjF3Q9rtkiUUgViYHdOqf3ic3PcbRIFc0FtuocHxMbLGaF1I8Y2MQFbuZe+hxZheNpLe8RZ9MvtSirEo4c4W90vcVFCvHUCy7nVn6pokLiSThyhNe5k+I5sgpzJPCXkx7xOndm9jkKFjGw3AUbzv3p92dMboFgkf2/lA2s9cI/BPudA0z2cUAAAAAASUVORK5CYII="

api_url = "https://api.api-ninjas.com/v1/imagetotext"
api_key = "h40kavMQcYc7U1rUbhA19lTCxZIp54XH41dBsThB"

# 1. Extract base64 payload if data URI prefix exists
if "," in image_url:
  base64_data = image_url.split(",")[1]
else:
  base64_data = image_url

# 2. Remove all whitespace and newline characters
base64_data = re.sub(r"\s+", "", base64_data)

# 3. Fix missing padding (=) if necessary
missing_padding = len(base64_data) % 4
if missing_padding:
  base64_data += "=" * (4 - missing_padding)

# 4. Decode into bytes cleanly
image_bytes = base64.b64decode(base64_data)

# 5. Send to API Ninjas
res = requests.post(
    api_url,
    headers={"X-Api-Key": api_key},
    files={"image": ("image.png", image_bytes, "image/png")},
)

print(res.json())
