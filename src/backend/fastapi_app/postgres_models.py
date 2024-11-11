from __future__ import annotations
from pgvector.sqlalchemy import Vector
from sqlalchemy import Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Document(Base):
    __tablename__ = "documents"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    document_title: Mapped[str] = mapped_column()
    page_number: Mapped[int] = mapped_column()
    document_date: Mapped[str] = mapped_column()  # Use DATE if you want strict date storage
    document_category: Mapped[str] = mapped_column()
    content: Mapped[str] = mapped_column()
    embedding_ada002: Mapped[Vector] = mapped_column(Vector(1536), nullable=True)  # ada-002 embedding

    def to_dict(self, include_embedding: bool = False):
        model_dict = {column.name: getattr(self, column.name) for column in self.__table__.columns}
        if include_embedding:
            model_dict["embedding_ada002"] = model_dict.get("embedding_ada002", [])
        else:
            del model_dict["embedding_ada002"]
        return model_dict

    def to_str_for_rag(self):
        return f"Title: {self.document_title} Category: {self.document_category} Content: {self.content[:200]}..."

    def to_str_for_embedding(self):
        return f"Title: {self.document_title} Category: {self.document_category} Content: {self.content[:200]}..."

table_name = Document.__tablename__

index_ada002 = Index(
    f"hnsw_index_for_innerproduct_{table_name}_embedding_ada002",
    Document.embedding_ada002,
    postgresql_using="hnsw",
    postgresql_with={"m": 16, "ef_construction": 64},
    postgresql_ops={"embedding_ada002": "vector_ip_ops"},
)
