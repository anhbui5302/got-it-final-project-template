from typing import List


def mask_sensitive_information(payload: dict, keys: List[str]):
    """Mask data that contains the key in `keys`"""
    for key in keys:
        if key in payload:
            payload[key] = '*' * 10
    # Recursively mask nested dict
    for key, value in payload.items():
        if isinstance(value, dict):
            payload[key] = mask_sensitive_information(value, keys)

    return payload
