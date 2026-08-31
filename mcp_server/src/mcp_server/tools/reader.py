import pathlib
import typing


class FileReader(typing.Protocol):
    def read(self, path: pathlib.Path) -> str:
        ...


class TextReader:
    def read(self, path: pathlib.Path) -> str:
        content = path.read_text(encoding="utf-8")

        return content


class MarkdownReader:
    def read(self, path: pathlib.Path) -> str:
        content = path.read_text(encoding="utf-8")

        return content


READERS: dict[str, type[FileReader]] = {
    ".txt": TextReader,
    ".md": MarkdownReader,
}


def get_reader(path: pathlib.Path) -> FileReader:
    reader_class = READERS.get(path.suffix.lower())

    if reader_class is None:
        raise ValueError(
            f"Unsupported file type: {path.suffix}"
        )

    return reader_class()

