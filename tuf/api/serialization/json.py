# Copyright New York University and the TUF contributors
# SPDX-License-Identifier: MIT OR Apache-2.0

"""TUF role metadata JSON serialization and deserialization.

This module provides concrete implementations to serialize and deserialize TUF
role metadata to and from the JSON wireline format for transportation, and
to serialize the 'signed' part of TUF role metadata to the OLPC Canonical JSON
format for signature generation and verification.

"""
import json

from securesystemslib.formats import encode_canonical

# pylint: disable=cyclic-import
# ... to allow de/serializing Metadata and Signed objects here, while also
# creating default de/serializers there (see metadata local scope imports).
# NOTE: A less desirable alternative would be to add more abstraction layers.
from tuf.api.metadata import Metadata, Signed
from tuf.api.serialization import (
    DeserializationError,
    MetadataDeserializer,
    MetadataSerializer,
    SerializationError,
    SignedSerializer,
)


class JSONDeserializer(MetadataDeserializer):
    """Provides JSON to Metadata deserialize method."""

    def deserialize(self, raw_data: bytes) -> Metadata:
        """Deserialize utf-8 encoded JSON bytes into Metadata object."""
        try:
            json_dict = json.loads(raw_data.decode("utf-8"))
            metadata_obj = Metadata.from_dict(json_dict)

        except Exception as e:
            raise DeserializationError from e

        return metadata_obj


class JSONSerializer(MetadataSerializer):
    """Provides Metadata to JSON serialize method.

    Attributes:
        compact: A boolean indicating if the JSON bytes generated in
                'serialize' should be compact by excluding whitespace.

    """

    def __init__(self, compact: bool = False) -> None:
        self.compact = compact

    def serialize(self, metadata_obj: Metadata) -> bytes:
        """Serialize Metadata object into utf-8 encoded JSON bytes."""
        try:
            indent = None if self.compact else 1
            separators = (",", ":") if self.compact else (",", ": ")
            json_bytes = json.dumps(
                metadata_obj.to_dict(),
                indent=indent,
                separators=separators,
                sort_keys=True,
            ).encode("utf-8")

        except Exception as e:
            raise SerializationError from e

        return json_bytes


class CanonicalJSONSerializer(SignedSerializer):
    """Provides Signed to OLPC Canonical JSON serialize method."""

    def serialize(self, signed_obj: Signed) -> bytes:
        """Serialize Signed object into utf-8 encoded OLPC Canonical JSON
        bytes.
        """
        try:
            signed_dict = signed_obj.to_dict()
            canonical_bytes = encode_canonical(signed_dict).encode("utf-8")

        except Exception as e:
            raise SerializationError from e

        return canonical_bytes
