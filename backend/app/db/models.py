from sqlalchemy import Column, Integer, Text, Boolean, ForeignKey, Index, Computed
from sqlalchemy.dialects.postgresql import UUID, JSONB, TSVECTOR
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
from app.config import settings
import uuid

Base = declarative_base()

class Statute(Base):
    __tablename__ = "statutes"

    id = Column(Integer, primary_key=True)
    act_name = Column(Text, nullable=False)
    section_number = Column(Text, nullable=False)
    title = Column(Text)
    text = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSONB, default=dict)
    embedding = Column(Vector(settings.embedding_dimension))
    
    # tsvector for search
    search_vector = Column(TSVECTOR, Computed("to_tsvector('english', coalesce(title, '') || ' ' || text)", persisted=True))

    __table_args__ = (
        Index("idx_statutes_search", "search_vector", postgresql_using="gin"),
        Index("idx_statutes_section", "act_name", "section_number", unique=True),
    )

class Debate(Base):
    __tablename__ = "debates"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(Text, nullable=False)
    act_name = Column(Text, nullable=False)
    student_position = Column(Text)

class Turn(Base):
    __tablename__ = "turns"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    debate_id = Column(UUID(as_uuid=True), ForeignKey("debates.id", ondelete="CASCADE"))
    role = Column(Text)
    content = Column(Text, nullable=False)
    citations = Column(JSONB, default=list)

class CitationCheck(Base):
    __tablename__ = "citation_checks"
    id = Column(Integer, primary_key=True)
    turn_id = Column(UUID(as_uuid=True), ForeignKey("turns.id", ondelete="CASCADE"))
    citation_text = Column(Text, nullable=False)
    verified = Column(Boolean, nullable=False)
    reason = Column(Text)
