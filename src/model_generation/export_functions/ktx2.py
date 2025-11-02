"""
KTX2 build helper using KTX-Software's `toktx` CLI.

Produces KTX2 textures for basecolor (sRGB) and normal (linear) maps.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import Literal

from ..utils.config import Config


def ensure_toktx() -> None:
    """Ensure `toktx` exists on PATH, else raise a clear error."""
    if not shutil.which("toktx"):
        raise RuntimeError(
            "toktx not found. Install KTX-Software and ensure it is on PATH."
        )


def build_ktx2(
    input_png: str | Path,
    output_ktx2: str | Path,
    *,
    is_normal: bool = False,
    quality: Literal["etc1s", "uastc"] = "etc1s",
    generate_mipmaps: bool = True,
) -> str:
    """
    Build a KTX2 file from a source PNG using `toktx`.

    Args:
        input_png: Source PNG path
        output_ktx2: Destination KTX2 path
        is_normal: True for normal map (linear + normal_map flag)
        quality: 'etc1s' for small compressed, 'uastc' for high quality
        generate_mipmaps: Whether to generate mipmaps

    Returns:
        The output KTX2 path as str
    """
    ensure_toktx()

    input_png = str(input_png)
    output_ktx2 = str(output_ktx2)

    args = ["toktx", "--t2"]
    if generate_mipmaps:
        args.append("--genmipmap")

    # Enforce target resolution to avoid NPOT/mipmap issues
    try:
        target_res = int(getattr(Config, "TEXTURE_RESOLUTION", 0))
    except Exception:
        target_res = 0
    if target_res:
        args += ["--resize", f"{target_res}x{target_res}"]

    if quality == "uastc":
        args += ["--encode", "uastc", "--zstd", "18"]
    else:
        args += ["--encode", "etc1s"]

    if is_normal:
        # Use normal_mode for linear normals; keeps two-channel XY by default.
        # If you want to keep 3 channels, consider adding: --input_swizzle rgb1
        args += ["--normal_mode", "--assign_oetf", "linear"]
    else:
        args += ["--assign_oetf", "srgb"]

    args += [output_ktx2, input_png]

    subprocess.run(args, check=True)

    if not Path(output_ktx2).exists():
        raise RuntimeError(f"KTX2 not created: {output_ktx2}")

    return output_ktx2


