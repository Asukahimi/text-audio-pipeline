# -*- coding: utf-8 -*-

import re
import json_to_lua


class LocalizationCfg:

    def __init__(self, keyname, data, config, properties, default_value):
        self.local_properties = properties
        self.default_value = default_value
        self.local_data = self.create_data(keyname, data, config)

    def update_default_value(self, data, default_value):
        for v in default_value:
            if not data.get(v):
                data[v] = default_value[v].get("value")

    def update_child_value(self, data, config, default_value):
        self.update_default_value(data, default_value)
        for v in config:
            name = v.get("Name")
            children = v.get("Children")
            value = data.get(name)
            if isinstance(value, str):
                del data[name]
            elif isinstance(value, dict):
                if children:
                    self.update_default_value(value,
                                              default_value.get("child"))
                    self.update_child_value(value, children)
            elif isinstance(value, list):
                if children:
                    for childv in value:
                        self.update_default_value(childv,
                                                  default_value.get("child"))
                        self.update_child_value(childv, children)
                else:
                    del data[name]
                    if len(value) == 1 and value[0] == "":
                        data["_{}Num".format(name)] = 0
                    else:
                        data["_{}Num".format(name)] = len(value)
        return data

    def create_item(self, data, config):
        item = {}

        for v in config:
            name = v.get("Name")
            children = v.get("Children")
            value = data.get(name)
            default_value = self.default_value.get(name)
            if None == value and default_value:
                value = default_value.get("value")

            if isinstance(value, str):
                continue
            elif isinstance(value, dict):
                if children:
                    self.update_child_value(value, children,
                                            default_value.get("value"))
                    item[name] = "\"{}\"".format(
                        re.sub(",}", "}",
                               json_to_lua.jsondata_to_lua_str(value)))
            elif isinstance(value, list):
                if children:
                    for childv in value:
                        self.update_child_value(childv, children,
                                                default_value.get("child"))
                    item[name] = "\"{}\"".format(
                        re.sub(",}", "}",
                               json_to_lua.jsondata_to_lua_str(value)))
                else:
                    if len(value) == 1 and value[0] == "":
                        item["_{}Num".format(name)] = 0
                    else:
                        item["_{}Num".format(name)] = len(value)

        return item

    def create_data(self, keyname, data, config):
        if not keyname or not data or not config:
            return

        local_data = {}

        for v in data:
            key = v.get(keyname)
            if not key:
                continue

            item = self.create_item(v, config)
            local_data[str(key)] = item

        return local_data

    def get_original_colname(self, colname):
        if colname.startswith("_"):
            colname = re.sub("^_", "", colname)
            colname = re.sub("Num$", "", colname)
        return colname

    def get_data_value(self, key, colname):
        if not self.is_localization_property(colname):
            return

        if not self.local_data:
            return

        data = self.local_data.get(key)
        if not data:
            return

        return data.get(colname)

    def get_property_info(self, colname, coltype):
        if not self.local_properties:
            return colname, coltype

        property = self.local_properties.get(colname)
        if not property:
            return colname, coltype

        if not property.get("bmsg"):
            if property.get("brepeated"):
                return "_{}Num".format(colname), property.get("coltype")
            else:
                return None, None

        return property.get("colname"), property.get("coltype")

    def is_repeated_str_property(self, colname):
        if not self.local_properties:
            return False

        colname = self.get_original_colname(colname)
        property = self.local_properties.get(colname)
        if not property:
            return False

        return property.get("brepeated") and not property.get("bmsg")

    def is_localization_property(self, colname):
        if not self.local_properties:
            return False

        colname = self.get_original_colname(colname)
        property = self.local_properties.get(colname)
        if not property:
            return False

        return True