import pathlib
import logging
import os

import mcp_server.tools.reader as mtrd
import mcp_server.config as mcfg

logger = logging.getLogger(__name__)


def write_article(finalDraft: str, filename: str = "article.md") -> dict:
    """
    use this function to write back the generated FinalDraft into disk

    Returns:
        dict: {
            "message": str,
            "file_path": str,
            "download_url": str
        }
    """

    safe_name = pathlib.Path(filename).name
    if pathlib.Path(safe_name).suffix not in {".md", ".txt", ".json"}:
        raise ValueError(f" un supported file type: {pathlib.Path(safe_name).suffix}")

    target_path = mcfg.OUTPUT_DIR / safe_name

    unique_path = get_unique_path(target_path)
    unique_path.write_text(finalDraft, encoding="utf-8")

    logger.info(f"[write_article] File written")

    # build the download link

    host = os.getenv("MCP_HOST", "localhost")
    port = os.getenv("MCP_PORT", "8000")
    download_url = f"http://{host}:{port}/files/{unique_path.name}"

    return {
        "message": f"file written: {unique_path.name}",
        "file_path": str(unique_path),
        "download_url": download_url
    }


def list_readable_files(subdir: str = ".") -> dict[str, list[str]]:
    """
    use this function to list all the readable files in the given directory path
    """

    safe_path = pathlib.Path(subdir)
    if ".." in safe_path.parts:
        raise ValueError("invalid path '..'")

    files = {}
    path = mcfg.DOCS_DIR / safe_path
    if not path.exists():
        raise FileNotFoundError(f"directory dose not exist: {subdir}")
    if not path.is_dir():
        raise ValueError(f"path is not a directory use read_note() instead: {subdir}")
    
    files["markdown_files"] = [str(p) for p in list(path.rglob("*.md"))]
    files["text_files"] = [str(p) for p in list(path.rglob("*.txt"))]

    return files


def get_unique_path(path: pathlib.Path) -> pathlib.Path:
    """
    create a serializaed copy instead of overwriting the existing file 
    """
    if not path.exists():
        return path

    i = 1
    while True:
        new_path = path.with_stem(f"{path.stem}_{i}")
        if not new_path.exists():
            return new_path
        i += 1


def read_file(path: str) -> str:
    """
    read the note and extract its content into a Document
    """

    safe_path = pathlib.Path(path)
    full_path = (mcfg.DOCS_DIR / safe_path).resolve()
    
    if not str(full_path).startswith(str(mcfg.DOCS_DIR.resolve())):
        raise ValueError(f"invalid path: {path}")    
    if not full_path.exists():
        raise FileNotFoundError(f"file dose not exist: {path}")
    if not full_path.is_file():
        raise ValueError(f"path dose not lead to file: {path}")

    reader = mtrd.get_reader(full_path)

    return reader.read(full_path)