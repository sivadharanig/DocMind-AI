from typing import List

class RecursiveTextChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", ". ", "? ", "! ", " ", ""]

    def chunk_text(self, text: str) -> List[str]:
        if not text or not text.strip():
            return []

        text = text.strip()
        if len(text) <= self.chunk_size:
            return [text]

        return self._recursive_split(text, self.separators)

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        final_chunks: List[str] = []
        separator = separators[-1]
        new_separators = []

        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break

        # Split text by separator
        splits = text.split(separator) if separator != "" else list(text)

        # Merge pieces into chunks of size <= chunk_size with overlap
        good_splits = []
        for s in splits:
            s_clean = s.strip()
            if s_clean:
                good_splits.append(s_clean)

        current_chunk = []
        current_len = 0

        for piece in good_splits:
            piece_len = len(piece) + (len(separator) if current_chunk else 0)

            if current_len + piece_len <= self.chunk_size:
                current_chunk.append(piece)
                current_len += piece_len
            else:
                if current_chunk:
                    chunk_merged = separator.join(current_chunk).strip()
                    if chunk_merged:
                        final_chunks.append(chunk_merged)
                    
                    # Compute overlap buffer
                    overlap_buffer = []
                    overlap_len = 0
                    for prev_piece in reversed(current_chunk):
                        if overlap_len + len(prev_piece) <= self.chunk_overlap:
                            overlap_buffer.insert(0, prev_piece)
                            overlap_len += len(prev_piece)
                        else:
                            break
                    current_chunk = overlap_buffer
                    current_len = sum(len(p) for p in current_chunk) + max(0, len(current_chunk) - 1) * len(separator)

                # If single piece itself is larger than chunk_size and we have deeper separators
                if len(piece) > self.chunk_size:
                    if new_separators:
                        sub_chunks = self._recursive_split(piece, new_separators)
                        final_chunks.extend(sub_chunks)
                    else:
                        # Hard character slice
                        for start in range(0, len(piece), self.chunk_size - self.chunk_overlap):
                            sub = piece[start:start + self.chunk_size].strip()
                            if sub:
                                final_chunks.append(sub)
                else:
                    current_chunk.append(piece)
                    current_len += len(piece) + (len(separator) if len(current_chunk) > 1 else 0)

        if current_chunk:
            last_chunk = separator.join(current_chunk).strip()
            if last_chunk and (not final_chunks or final_chunks[-1] != last_chunk):
                final_chunks.append(last_chunk)

        return [c for c in final_chunks if c.strip()]
