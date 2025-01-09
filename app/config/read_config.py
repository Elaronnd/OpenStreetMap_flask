from yaml import safe_load

with open("app/config/config.yaml", 'r') as file:
    data_from_file = safe_load(file)

ACCESS_TOKEN_IPINFO = data_from_file["ACCESS_TOKEN_IPINFO"]
