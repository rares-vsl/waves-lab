from enum import Enum

class NodeType(str, Enum):
    """Supported utility types for WaveNodes."""
    ELECTRICITY = "ELECTRICITY"
    WATER = "WATER"
    GAS = "GAS"