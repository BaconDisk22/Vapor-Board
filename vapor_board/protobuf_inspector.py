"""Optional read-only FromRadio protobuf inspection via installed Meshtastic schemas."""


class ProtobufUnavailable(RuntimeError):
    pass


def parse_from_radio(payload, schema=None):
    """Parse one framed payload; does not validate identity or protocol session."""
    if not isinstance(payload, (bytes, bytearray)) or not payload:
        raise ValueError("nonempty protobuf payload required")
    if schema is None:
        try:
            from meshtastic.protobuf import mesh_pb2
        except ImportError as exc:
            raise ProtobufUnavailable("Install a compatible meshtastic Python package") from exc
        schema = mesh_pb2.FromRadio
    message = schema()
    message.ParseFromString(bytes(payload))
    return message


def describe_from_radio(message):
    """Minimal metadata only: avoid dumping potentially private message contents."""
    variant = message.WhichOneof("payload_variant")
    return {"variant": variant or "unknown"}
