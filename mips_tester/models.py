"""
Defined data models for MIPS testing library
"""

from enum import Enum
from pydantic import BaseModel, Field, validator


class JumpType(str, Enum):
    """Type of jump instruction to use in harness."""

    JUMP = "j"
    JUMP_AND_LINK = "jal"


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

    class Config:
        validate_assignment = True


class MipsState(BaseModel):
    """Represents the complete state of a MIPS program (registers+memory)."""

    registers: RegisterState = Field(default_factory=RegisterState)
    memory: dict[str, str] = Field(
        default_factory=dict,
        description="Memory address to value mappings (decimal or Hex)",
    )

    @validator("memory")
    def validate_memory_addresses(cls, v):
        memory = dict()
        for addr, val in v.items():
            # ensure address is string:
            addr_str = str(addr)

            # ensure address is number (decimal or hex):
            try:
                addr_int = int(addr_str, 0)
                addr_padded = f"0x{addr_int:08x}"
            except ValueError:
                raise ValueError(
                    f"Invalid memory address: {addr_str}! Must be decimal or hex"
                )

            # ensure val is a string:
            val_str = str(val)

            # ensure value is number (decimal or hex):
            try:
                int(val_str, 0)
            except ValueError:
                raise ValueError(
                    f"Invalid memory value: {val_str}! Must be decimal or hex"
                )
            memory[addr_padded] = val_str
        return memory

    class Config:
        validate_assignment = True


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
