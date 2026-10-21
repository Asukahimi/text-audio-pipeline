import re


def jsondata_to_lua_str(data, iskey=False):
    if isinstance(data, (int, float)):
        return str(data)
    elif isinstance(data, str):
        if iskey or re.match("^{[\w\W]*}$", data):
            return "{}".format(data)
        else:
            return "\"\"{}\"\"".format(data)

    elif isinstance(data, list):
        temp_str = "{"
        for one_data in data:
            temp_str += "{},".format(jsondata_to_lua_str(one_data, False))
        temp_str += "}"
        return temp_str
    elif isinstance(data, dict):
        temp_str = "{"
        for key in data.keys():
            temp_str += "{}={},".format(jsondata_to_lua_str(key, True),
                                        jsondata_to_lua_str(data[key], False))
        temp_str += "}"
        return temp_str

    return "nil"