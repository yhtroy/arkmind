"""Asset type enumeration (Asset Contract v1).

Frozen v1 set: only CONCEPT / DEFINITION / QUOTE. No reserved values; new
types are added by amending the contract, not by pre-allocating here.
"""

from __future__ import annotations

from enum import Enum


class AssetType(str, Enum):
    CONCEPT = "CONCEPT"
    DEFINITION = "DEFINITION"
    QUOTE = "QUOTE"
