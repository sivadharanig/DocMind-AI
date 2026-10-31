import io
import re
from abc import ABC, abstractmethod

class BaseParser(ABC):
    @abstractmethod
    def extract_text(self, file_bytes: bytes) -> str:
        """Extract clean text content from binary stream."""
        pass

    def clean_text(self, text: str) -> str:
        """Normalizes text by removing non-printable/control characters and regularizing whitespace."""
        if not text:
            return ""
        # Remove null bytes and non-printable control characters (except newline and tab)
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        # Normalize carriage returns
        text = text.replace('\r\n', '\n').replace('\r', '\n')
        # Collapse excessive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

class PDFParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            extracted_pages = []
            for idx, page in enumerate(reader.pages):
                page_text = page.extract_text() or ""
                if page_text.strip():
                    extracted_pages.append(page_text)
            full_text = "\n\n".join(extracted_pages)
            return self.clean_text(full_text)
        except Exception as e:
            raise ValueError(f"Failed to parse PDF document: {str(e)}")

class DocxParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                    if row_text:
                        paragraphs.append(row_text)
            full_text = "\n\n".join(paragraphs)
            return self.clean_text(full_text)
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX document: {str(e)}")

class PlainTextParser(BaseParser):
    def extract_text(self, file_bytes: bytes) -> str:
        try:
            full_text = file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            full_text = file_bytes.decode("latin-1", errors="replace")
        return self.clean_text(full_text)

class ParserFactory:
    _parsers = {
        ".pdf": PDFParser,
        ".docx": DocxParser,
        ".txt": PlainTextParser,
    }

    @classmethod
    def get_parser_for_extension(cls, ext: str) -> BaseParser:
        normalized_ext = ext.lower().strip()
        if not normalized_ext.startswith("."):
            normalized_ext = "." + normalized_ext
            
        parser_cls = cls._parsers.get(normalized_ext)
        if not parser_cls:
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats: PDF, DOCX, TXT")
        return parser_cls()
