from typing import List

import langchain_text_splitters

import itisamanager.schema as isma
import itisamanager.config.settings as iset


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


def semantic_deduplicate(chunks: List[isma.KnowledgeChunk], threshold: float = 0.85) -> List[isma.KnowledgeChunk]:

    if len(chunks) <= 1:
        return chunks

    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    # "all-MiniLM-L6-v2"
    model = iset.get_EMBEDDING_MODEL()

    summaries = [chunk.summary for chunk in chunks]

    # Convert all summaries into embedding vectors.
    #
    # If there are n chunks, the resulting array has shape:
    # (n, 384)
    emb = model.encode(summaries)

    kept_indices = []

    # Greedy deduplication:
    for i in range(len(chunks)):
        is_dup = False

        if kept_indices:

            sim = cosine_similarity([emb[i]], emb[kept_indices])[0]

            # If the current chunk is sufficiently similar to
            # ANY previously kept chunk, consider it a duplicate.
            if any(s >= threshold for s in sim):
                is_dup = True

                # Find the previously kept chunk with the highest
                # similarity to the current chunk.
                first_idx = kept_indices[np.argmax(sim)]

                # Merge the key terms from both chunks.
                old_terms = set(chunks[first_idx].key_terms.split(", "))
                new_terms = set(chunks[i].key_terms.split(", "))
                chunks[first_idx].key_terms = ", ".join(sorted(old_terms | new_terms))

        # If the current chunk is not a duplicate,
        # keep its index for the final result.
        if not is_dup:
            kept_indices.append(i)

    # Return only the chunks that survived deduplication.
    return [chunks[i] for i in kept_indices]


def select_relevant_files(file_paths: List[str], query: str, top_k: int = 5, threshold: float = 0.1) -> List[str]:

    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    # "all-MiniLM-L6-v2"
    model = iset.get_EMBEDDING_MODEL()

    file_summaries = []

    for path in file_paths:
        try:
            content = read_file(path).content[:1000]
            file_summaries.append(content)

        except Exception:
            file_summaries.append("")

    # Convert the query into an embedding vector.
    #
    # The result has shape (1, 384) because there is one query
    # and the model produces a 384-dimensional embedding.
    query_emb = model.encode([query])

    # Convert all file summaries into embedding vectors.
    #
    # If there are N files, the result has shape (N, 384).
    file_embs = model.encode(file_summaries)

    # Calculate the cosine similarity between the query embedding
    # and every file embedding.
    #
    # The result has shape (1, N), because there is one query
    # and N file summaries.
    similarities = cosine_similarity(query_emb, file_embs)[0]

    top_indices = np.argsort(similarities)[-top_k:]
    top_indices = top_indices[::-1]

    return [
        file_paths[i]
        for i in top_indices
        if similarities[i] > threshold
    ]