from yaml import safe_load

with open("app/config/config.yaml", 'r') as file:
    data_from_file = safe_load(file)

ACCESS_TOKEN_IPINFO = data_from_file["ACCESS_TOKEN_IPINFO"]
EMAIL = data_from_file["EMAIL"]
TOKEN_EMAIL = data_from_file["TOKEN_EMAIL"]
UPLOAD_FOLDER = data_from_file["UPLOAD_FOLDER"]
SECRET_KEY = data_from_file["SECRET_KEY"]
