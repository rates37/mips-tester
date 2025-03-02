"""
Contains core functionality for the MIPS testing library.
Includes configuration and shared utils
"""

from pydantic import BaseModel, Field
from pathlib import Path


class MipsConfig(BaseModel):
    """
    Configuration for the MIPS tester environment.
    """

    mars_path: Path = Field(
        default=Path("mars.jar"),
        description="Path to the MIPS mars jar executable file",
    )
    default_max_steps: int = Field(
        default=10000,
        description="Default maximum number of steps to simulate MIPS programs for",
    )
    default_output_harness: str = Field(
        default="harness.asm", description="Default output filename for test harness"
    )

    class Config:
        validate_assignment = True


# Global config instance:
config = MipsConfig()


def configure(
    mars_path: str | None, max_steps: int | None, output_harness: str | None
) -> None:
    """Updates global config for MIPS tester

    Args:
        mars_path (str | None): Path to Mars JAR file
        max_steps (int | None): Default maximum number of steps to simulate for
        output_harness (str | None): Default harness filename
    """
    global config

    if mars_path is not None:
        config.mars_path = Path(mars_path)

    if max_steps is not None:
        config.default_max_steps = max_steps

    if output_harness is not None:
        config.default_output_harness = output_harness
