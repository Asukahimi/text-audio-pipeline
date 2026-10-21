# -*- coding: utf-8 -*-

# from enum import IntEnum

# class ProtoCppType(IntEnum):
#     CPPTYPE_INT32 = 1
#     CPPTYPE_INT64 = 2
#     CPPTYPE_UINT32 = 3
#     CPPTYPE_UINT64 = 4
#     CPPTYPE_DOUBLE = 5
#     CPPTYPE_FLOAT = 6
#     CPPTYPE_BOOL = 7
#     CPPTYPE_ENUM = 8
#     CPPTYPE_STRING = 9
#     CPPTYPE_MESSAGE = 10
#     MAX_CPPTYPE = 10

# class ProtoLabelType(IntEnum):
#     LABEL_OPTIONAL = 1
#     LABEL_REQUIRED = 2
#     LABEL_REPEATED = 3
#     MAX_LABEL = 3

CPPTYPE_INT32 = 1
CPPTYPE_INT64 = 2
CPPTYPE_UINT32 = 3
CPPTYPE_UINT64 = 4
CPPTYPE_DOUBLE = 5
CPPTYPE_FLOAT = 6
CPPTYPE_BOOL = 7
CPPTYPE_ENUM = 8
CPPTYPE_STRING = 9
CPPTYPE_MESSAGE = 10
MAX_CPPTYPE = 10

LABEL_OPTIONAL = 1
LABEL_REQUIRED = 2
LABEL_REPEATED = 3
MAX_LABEL = 3


def find_message_types_internal(protoname, fieldname, proto_define):
    if protoname not in proto_define.DESCRIPTOR.message_types_by_name:
        return

    message_types = proto_define.DESCRIPTOR.message_types_by_name[protoname]
    if not fieldname:
        return message_types

    field = message_types.fields_by_name.get(fieldname)
    if not field:
        return

    return field.message_type


def find_message_types(protoname, fieldname):
    import proto_res_c_pb2
    import proto_res_dasheng_c_pb2
    import proto_res_lightpaw_c_pb2
    client_proto_define_list = [
        proto_res_c_pb2, proto_res_dasheng_c_pb2, proto_res_lightpaw_c_pb2
    ]
    for v in client_proto_define_list:
        ret = find_message_types_internal(protoname, fieldname, v)
        if ret:
            return ret


def get_default_value_by_message_types(message_types):
    default_value = {}
    for field_desc in message_types.fields:
        if field_desc.cpp_type == CPPTYPE_MESSAGE:
            field_message_type = message_types.fields_by_name[
                field_desc.name].message_type
            child = get_default_value_by_message_types(field_message_type)
            if field_desc.label == LABEL_REPEATED:
                default_value[field_desc.name] = {
                    "value": field_desc.default_value,
                    "child": child
                }
            else:
                field_message_type = message_types.fields_by_name[
                    field_desc.name].message_type
                default_value[field_desc.name] = {
                    "value": child,
                }
        else:
            default_value[field_desc.name] = {
                "value": field_desc.default_value
            }

    return default_value


def get_default_value(protoname, fieldname=None):
    message_types = find_message_types(protoname, fieldname)
    return get_default_value_by_message_types(message_types)

def find_cpp_type_internal(protoname, fieldname, proto_define):
    if protoname not in proto_define.DESCRIPTOR.message_types_by_name:
        return

    message_types = proto_define.DESCRIPTOR.message_types_by_name[protoname]
    if not fieldname:
        return message_types

    field = message_types.fields_by_name.get(fieldname)
    if not field:
        return

    return field.cpp_type

def get_cpp_type(protoname, fieldname):
    import proto_res_c_pb2
    import proto_res_dasheng_c_pb2
    import proto_res_lightpaw_c_pb2

    client_proto_define_list = [
        proto_res_c_pb2, proto_res_dasheng_c_pb2, proto_res_lightpaw_c_pb2
    ]

    for v in client_proto_define_list:
        ret = find_cpp_type_internal(protoname, fieldname, v)
        if ret:
            return ret