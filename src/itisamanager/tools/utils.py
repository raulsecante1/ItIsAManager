import pathlib


import langchain_text_splitters

import itisamanager.tools.reader as irdr
import itisamanager.schema as isma
import itisamanager.config.settings as iset


def read_file(path: str) -> isma.Document:
    """
    read the note and extract its content into a Document
    """

    file_path = pathlib.Path(path)

    if not file_path.exists():
        raise FileNotFoundError(path)

    reader = irdr.get_reader(file_path)

    return reader.read(file_path)


def chunking(sourcefile: isma.Document) -> list[isma.ChunkText]:
    """
    chop the document into chunks
    """
    splitter = langchain_text_splitters.RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
    )

    chunks = splitter.split_text(sourcefile.content)

    output_chunk = []

    for index, chunk in enumerate(chunks):
        output_chunk.append(
            isma.ChunkText(
                content=chunk,
                source=sourcefile.source,
                index=index,
            )
        )

    return output_chunk