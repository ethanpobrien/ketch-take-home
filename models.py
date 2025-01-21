from __future__ import annotations

from datetime import datetime
from typing import Literal, get_args, Optional, List

from pydantic import BaseModel, Field
from sqlalchemy import String, ForeignKey, Enum, func, Column, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


AnswerType = Literal["single_select", "multiple_select"]


class Base(DeclarativeBase):
    pass


class OrganizationIn(BaseModel):
    name: str


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(),
        onupdate=func.CURRENT_TIMESTAMP()
    )

    name: Mapped[str] = mapped_column(String(60))


question_question_set_table = Table(
    "question_question_set_table",
    Base.metadata,
    Column("question_set_id", ForeignKey("question_set.id"), primary_key=True),
    Column("question_id", ForeignKey("question.id"), primary_key=True),
)


class QuestionSetIn(BaseModel):
    organization_id: int
    name: str
    active: Optional[bool]
    question_ids: List[int]

class QuestionSetUpdateIn(BaseModel):
    name: str
    active: Optional[bool]
    question_ids: List[int]


class QuestionSet(Base):
    __tablename__ = "question_set"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(),
        onupdate=func.CURRENT_TIMESTAMP()
    )

    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"))
    questions: Mapped[List[Question]] = relationship(
        secondary=question_question_set_table, back_populates="question_set"
    )
    name: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(default=False)

class QuestionIn(BaseModel):
    question_text: str
    organization_id: int
    question_set_id: Optional[int] = Field(None)
    answer_type: Optional[AnswerType] = Field(None)

class QuestionUpdateIn(BaseModel):
    question_text: str
    question_set_id: Optional[int] = Field(None)


class Question(Base):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(),
        onupdate=func.CURRENT_TIMESTAMP()
    )

    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"))
    # question_set_id: Mapped[int] = mapped_column(ForeignKey("question_set.id"), nullable=True)
    question_set: Mapped[List[QuestionSet]] = relationship(
        secondary=question_question_set_table, back_populates="questions"
    )



    question_text: Mapped[str] = mapped_column(String(300))

    # Ref: https://stackoverflow.com/a/76277425
    answer_type: Mapped[AnswerType] = mapped_column(Enum(
        *get_args(AnswerType),
        name="answer_type",
        create_constraint=True,
        validate_strings=True,
    ))


class AnswerIn(BaseModel):
    answer_text: str
    question_id: int

class AnswerUpdateIn(BaseModel):
    answer_text: str


class Answer(Base):
    __tablename__ = "answer"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(),
        onupdate=func.CURRENT_TIMESTAMP()
    )

    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"))
    answer_text: Mapped[str] = mapped_column(String(100))


class Migration(Base):
    """
    Special database table for tracking if migrations have been run
    """
    __tablename__ = "migration"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )

    name: Mapped[str] = mapped_column(String(100))
    migrated: Mapped[bool] = mapped_column(default=False)