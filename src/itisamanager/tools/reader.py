import pathlib
import typing

import itisamanager.schema as isma


class FileReader(typing.Protocol):
    def read(self, path: pathlib.Path) -> isma.Document:
        ...


class TextReader:
    def read(self, path: pathlib.Path) -> isma.Document:
        content = path.read_text(encoding="utf-8")

        return isma.Document(
            content=content,
            source=str(path),
        )


class MarkdownReader:
    def read(self, path: pathlib.Path) -> isma.Document:
        content = path.read_text(encoding="utf-8")

        return isma.Document(
            content=content,
            source=str(path),
        )


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

