import pathlib
from typing import List
from pathlib import Path

import langchain_text_splitters

import itisamanager.tools.reader as irdr
import itisamanager.schema as isma


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


def get_unique_path(path: Path) -> Path:
    """
    create a serializaed copy in stead of overwriting the existing file
    """
    if not path.exists():
        return path

    i = 1
    while True:
        new_path = path.with_stem(f"{path.stem}_{i}")
        if not new_path.exists():
            return new_path
        i += 1


def semantic_deduplicate(chunks: List[isma.KnowledgeChunk]) -> List[isma.KnowledgeChunk]:
    """
    use an embedding model to deduplicate the semantically alike chunks
    """

    return chunks

    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode([c.summary for c in chunks])
    
    unique = []
    for i, c in enumerate(chunks):
        is_dup = False
        for j in unique_indices:
            if cosine_sim(embeddings[i], embeddings[j]) > 0.85:
                is_dup = True
                break
        if not is_dup:
            unique.append(c)
    return unique