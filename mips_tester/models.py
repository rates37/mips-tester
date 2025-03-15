"""
Defined data models for MIPS testing library
"""

from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, field_validator


class JumpType(str, Enum):
    """Type of jump instruction to use in harness."""

    JUMP = "j"
    JUMP_AND_LINK = "jal"


class MemorySize(str, Enum):
    """Size of memory to access."""

    BYTE = "byte"  # 1 byte
    HALFWORD = "half"  # 2 bytes
    WORD = "word"  # 4 bytes


class MemoryEntry(BaseModel):
    """Represents a single memory entry with size and value."""

    value: str
    size: MemorySize = MemorySize.WORD

    @field_validator("value")
    def validate_value(cls, v):
        val_str = str(v)
        # ensure decimal or hex:
        try:
            int(val_str, 0)
        except ValueError:
            raise ValueError(f"Invalid memory value: {val_str}! Must be decimal or hex")
        return val_str

    model_config = ConfigDict(validate_assignment=True)


class RegisterState(BaseModel):
    """Represents the state of MIPS registers"""

    v0: str | None = None
    v1: str | None = None
    a0: str | None = None
    a1: str | None = None
    a2: str | None = None
    a3: str | None = None
    t0: str | None = None
    t1: str | None = None
    t2: str | None = None
    t3: str | None = None
    t4: str | None = None
    t5: str | None = None
    t6: str | None = None
    t7: str | None = None
    t8: str | None = None
    t9: str | None = None
    s0: str | None = None
    s1: str | None = None
    s2: str | None = None
    s3: str | None = None
    s4: str | None = None
    s5: str | None = None
    s6: str | None = None
    s7: str | None = None

    model_config = ConfigDict(validate_assignment=True)


class MipsState(BaseModel):
    """Represents the complete state of a MIPS program (registers+memory)."""

    registers: RegisterState = Field(default_factory=RegisterState)
    memory: dict[str, MemoryEntry] = Field(
        default_factory=dict,
        description="Memory address to value mappings with size specification",
    )

    @field_validator("memory")
    def validate_memory_addresses(cls, v):
        memory = dict()
        for addr, entry in v.items():
            # ensure entry is MemoryEntry:
            if isinstance(entry, dict):
                memory_entry = MemoryEntry(**entry)

            elif isinstance(entry, str) or isinstance(entry, int):
                # default to WORD size entry
                memory_entry = MemoryEntry(value=str(entry))

            elif isinstance(entry, MemoryEntry):
                memory_entry = entry
            else:
                raise ValueError(f"Invalid memory entry type for {addr}: {type(entry)}")
            # ensure address is string:
            addr_str = str(addr)

            # ensure address is number (decimal or hex):
            try:
                addr_int = int(addr_str, 0)

                # ensure memory address is aligned with word or half word boundaries:
                if memory_entry.size == MemorySize.HALFWORD and addr_int % 2 != 0:
                    raise ValueError(
                        f"Halfword address {addr_str} must be 2-byte aligned"
                    )
                elif memory_entry.size == MemorySize.WORD and addr_int % 4 != 0:
                    raise ValueError(f"Word address {addr_str} must be 4-byte aligned")

                addr_padded = f"0x{addr_int:08x}"
            except ValueError:
                raise ValueError(
                    f"Invalid memory address: {addr_str}! Must be decimal or hex"
                )

            memory[addr_padded] = memory_entry
        return memory

    # backward compatibility for easy dict initialisation:
    @classmethod
    def from_dict(cls, data: dict):
        """Create MipsState from dictionary with backward compatibility."""
        if "memory" in data and isinstance(data["memory"], dict):
            memory_dict = dict()
            for addr, value in data["memory"].items():
                if isinstance(value, dict) and "value" in value:
                    # already in new format:
                    memory_dict[addr] = value
                else:
                    # uses old format, so convert to new format
                    # with default as WORD size
                    memory_dict[addr] = {"value": str(value), "size": MemorySize.WORD}
            data["memory"] = memory_dict
        return cls(**data)

    model_config = ConfigDict(validate_assignment=True)


class TestResult(BaseModel):
    """The results of running a MIPS test."""

    success: bool
    score: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Proportion of passed checks"
    )
    messages: list[str] = Field(
        default_factory=list,
        description="List of feedback messages from running checks",
    )
