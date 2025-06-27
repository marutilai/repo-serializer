"""File processing utilities for different file types."""

import json
import os


def process_jupyter_notebook(file_path):
    """Process Jupyter notebook files."""
    with open(file_path, "r", encoding="utf-8") as f:
        try:
            notebook = json.load(f)
            cells_content = []

            # Add notebook metadata if available
            if (
                "metadata" in notebook
                and "kernelspec" in notebook["metadata"]
            ):
                kernel = notebook["metadata"]["kernelspec"].get(
                    "display_name", "Unknown"
                )
                cells_content.append(
                    f"Jupyter Notebook (Kernel: {kernel})\n"
                )

            # Process cells - don't limit the number of cells
            for i, cell in enumerate(notebook.get("cells", [])):
                cell_type = cell.get("cell_type", "unknown")

                if cell_type == "markdown":
                    source = "".join(cell.get("source", []))
                    cells_content.append(
                        f"[Markdown Cell {i+1}]\n{source}\n"
                    )

                elif cell_type == "code":
                    source = "".join(cell.get("source", []))
                    # Don't limit code cells, show all code
                    cells_content.append(
                        f"[Code Cell {i+1}]\n{source}\n"
                    )

                    # Include a sample of outputs if present, but limit these
                    outputs = cell.get("outputs", [])
                    if outputs:
                        output_text = []
                        # Only show first output and limit its size
                        if outputs:
                            output = outputs[0]
                            if "text" in output:
                                text = "".join(output["text"])
                                # Limit output text to 3 lines
                                if len(text.splitlines()) > 3:
                                    text_lines = text.splitlines()[
                                        :3
                                    ]
                                    text = "\n".join(text_lines)
                                    text += "\n... [output truncated] ..."
                                output_text.append(text)
                            elif (
                                "data" in output
                                and "text/plain" in output["data"]
                            ):
                                text = "".join(
                                    output["data"]["text/plain"]
                                )
                                # Limit output text to 3 lines
                                if len(text.splitlines()) > 3:
                                    text_lines = text.splitlines()[
                                        :3
                                    ]
                                    text = "\n".join(text_lines)
                                    text += "\n... [output truncated] ..."
                                output_text.append(text)

                        if output_text:
                            cells_content.append(
                                "Output (sample):\n"
                                + "\n".join(output_text)
                                + "\n"
                            )

                        if len(outputs) > 1:
                            cells_content.append(
                                f"... [{len(outputs) - 1} more outputs not shown] ...\n"
                            )

            return "\n".join(cells_content)
        except json.JSONDecodeError:
            return "[Invalid or corrupted notebook file]"


def process_csv_file(file_path, max_lines=5):
    """Process CSV files, showing only first few lines."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = []
        for i, line in enumerate(f):
            if i >= max_lines:
                lines.append(
                    "... [remaining CSV content truncated] ..."
                )
                break
            lines.append(line.rstrip())
        return "\n".join(lines)


def process_text_file(file_path, max_lines=1000):
    """Process regular text files with optional line limit."""
    with open(file_path, "r", encoding="utf-8") as f:
        lines = []
        for i, line in enumerate(f):
            if i >= max_lines:
                lines.append(
                    f"\n... [file truncated after {max_lines} lines] ..."
                )
                break
            lines.append(line.rstrip())

        if len(lines) >= max_lines:
            return "\n".join(lines)
        else:
            f.seek(0)
            return f.read()