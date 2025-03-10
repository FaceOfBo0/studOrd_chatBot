def paragraphs_chunks(sect: dict) -> list[str]:
    """Legacy method for compatibility"""
    documents = []
    for _, sec in sect.items():
        for item in parse_paragraphs(sec):
            documents.append(item)
    return documents


def parse_paragraphs(text: str) -> list[str]:
        """Legacy method for compatibility"""
        lines = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for line in lines:
            if line.startswith('§'):
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line
            else:
                current_chunk += " " + line

        if current_chunk:
            chunks.append(current_chunk.strip())
        if len(chunks) > 1:
            chunks[0] = chunks[0] + " " + chunks[1]
            chunks.remove(chunks[1])
        return chunks