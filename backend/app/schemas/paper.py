from pydantic import BaseModel, Field


class Section(BaseModel):
    title: str
    text: str
    page_start: int
    page_end: int


class PageContent(BaseModel):
    page_number: int
    text: str


class FigureItem(BaseModel):
    label: str
    page_number: int
    caption: str = ""
    note: str = "TODO: basic figure extraction placeholder"


class TableItem(BaseModel):
    label: str
    page_number: int
    caption: str = ""
    note: str = "TODO: basic table extraction placeholder"


class ParsedPaper(BaseModel):
    paper_id: str
    title: str
    authors: list[str] = Field(default_factory=list)
    abstract: str
    sections: list[Section] = Field(default_factory=list)
    pages: list[PageContent] = Field(default_factory=list)
    figures: list[FigureItem] = Field(default_factory=list)
    tables: list[TableItem] = Field(default_factory=list)
    references: list[str] = Field(default_factory=list)
