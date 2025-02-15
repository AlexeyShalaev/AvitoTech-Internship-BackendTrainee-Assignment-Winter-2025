from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message


def message_to_dict(message: Message) -> dict:
    return MessageToDict(
        message,
        always_print_fields_with_no_presence=True,
        preserving_proto_field_name=True,
    )
