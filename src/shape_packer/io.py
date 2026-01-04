"""File I/O for shape packer.

Handles parsing input files and writing solution output.

Input file format:
    height width
    D1,R2,U1      # Shape 1
    L3,D2,R1,U3   # Shape 2
    ...

Output format:
    column,row,rotation  # For each shape in order

Example:
    shapes, dims = parse_input_file(Path("input.txt"))
    write_solution(Path("output.txt"), solution, elapsed_time)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple

from shape_packer.individual import Individual
from shape_packer.shape import Shape


def parse_input_file(filepath: Path) -> Tuple[List[Shape], Tuple[int, int]]:
    """Parse an input file to extract shapes and board dimensions.

    Input format:
        height [num_shapes]     # First line, second value ignored
        D1,R2,U1               # Shape instructions (comma or space separated)
        L3 R2 D1               # Alternative format with spaces
        ...

    Board width is calculated as sum of max(shape_width, shape_height)
    for all shapes. This matches the original college code behavior.

    Args:
        filepath: Path to the input file.

    Returns:
        Tuple of (list of shapes, (width, height)).

    Raises:
        FileNotFoundError: If file doesn't exist.
        ValueError: If file format is invalid.
    """
    with open(filepath, "r") as f:
        lines = f.readlines()

    if not lines:
        raise ValueError("Input file is empty")

    # First line: height [ignored_value]
    first_line = lines[0].strip().split()
    if not first_line:
        raise ValueError(f"First line is empty: {lines[0].strip()}")

    try:
        height = int(first_line[0])
    except ValueError as e:
        raise ValueError(f"Invalid height: {e}") from e

    # Remaining lines: shape instructions
    shapes: List[Shape] = []
    for i, line in enumerate(lines[1:], start=1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        shape = Shape.from_instructions(line, shape_id=i - 1)
        shapes.append(shape)

    # Calculate width as sum of shape bounding boxes (original behavior)
    width = sum(max(s.bounding_box) for s in shapes)

    return shapes, (width, height)


def write_solution(
    filepath: Path,
    solution: Individual,
    elapsed_time: float | None = None,
) -> None:
    """Write a solution to a file.

    Output format: column,row,rotation for each shape (sorted by shape_id).

    Args:
        filepath: Path to output file.
        solution: Solution to write.
        elapsed_time: Optional elapsed time in seconds.
    """
    # Sort placements by shape_id
    sorted_placements = sorted(
        solution.placements,
        key=lambda p: p.shape.shape_id,
    )

    with open(filepath, "w") as f:
        if elapsed_time is not None:
            f.write(f"# Elapsed time: {elapsed_time:.3f}s\n")
            f.write(f"# Fitness: {solution.fitness:.2f}\n")
            f.write("#\n")

        for placement in sorted_placements:
            f.write(
                f"{placement.position.col},{placement.position.row},"
                f"{placement.rotation}\n"
            )


def format_solution(solution: Individual) -> str:
    """Format a solution as a string for display.

    Args:
        solution: Solution to format.

    Returns:
        Formatted string.
    """
    lines = [f"Fitness: {solution.fitness:.2f}"]
    lines.append(f"Shapes: {len(solution.placements)}")
    lines.append("")
    lines.append("Placements (col, row, rotation):")

    sorted_placements = sorted(
        solution.placements,
        key=lambda p: p.shape.shape_id,
    )
    for placement in sorted_placements:
        lines.append(
            f"  Shape {placement.shape.shape_id}: "
            f"({placement.position.col}, {placement.position.row}, "
            f"rot={placement.rotation})"
        )

    return "\n".join(lines)
