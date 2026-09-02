import langchain_text_splitters

import itisamanager.schema as isma

import pathlib


def chunking(sourcefile: str) -> list[isma.ChunkText]:
    """
    chop the content into chunks
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
                index=index,
            )
        )

    return output_chunk


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