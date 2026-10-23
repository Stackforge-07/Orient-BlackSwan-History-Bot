"""Offline, page-preserving extraction; never silently OCR or invent text."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def extract_pages(path: Path) -> list[Document]:
    reader = PdfReader(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    pages = []
    for index, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        # Embedded PDF labels are not necessarily visibly printed on the page.
        label = reader.page_labels[index]
        match = re.search(r"(?:HISTORY\s+(\d+)\b|\b(\d+)\s+HISTORY)", text)
        printed = next((g for g in match.groups() if g), "") if match else ""
        section = ""
        for heading in ("AUTHOR INDEX", "TITLE INDEX", "CONTENTS", "HISTORY"):
            if re.search(r"\b" + heading + r"\b", text):
                section = heading.title()
                break
        pages.append(Document(page_content=text, metadata={
            "pdf_page": index + 1,
            "pdf_label": label,
            "printed_page": printed,
            "section": section,
            "source": path.name,
            "document_hash": digest,
            "extractor": "pypdf",
        }))
    return pages


def chunk_pages(pages: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)
    chunks = []
    for page in pages:
        for index, chunk in enumerate(splitter.split_documents([page])):
            identity = f"{page.metadata['document_hash']}:{page.metadata['pdf_page']}:{index}:{chunk.page_content}"
            chunk.metadata["chunk_id"] = hashlib.sha256(identity.encode()).hexdigest()
            chunks.append(chunk)
    covered = {c.metadata["pdf_page"] for c in chunks}
    expected = {p.metadata["pdf_page"] for p in pages if p.page_content.strip()}
    if covered != expected:
        raise ValueError("Chunk coverage does not match pages with extractable text.")
    return chunks
