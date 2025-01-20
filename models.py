from datetime import datetime
from typing import Literal
from typing import get_args

from sqlalchemy import String, ForeignKey, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


AnswerType = Literal["single_select", "multiple_select"]


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )

    name: Mapped[str] = mapped_column(String(60))


class QuestionSet(Base):
    __tablename__ = "question_set"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(), onupdate=func.CURRENT_TIMESTAMP()
    )

    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"))
    name: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(default=False)


class Question(Base):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(), onupdate=func.CURRENT_TIMESTAMP()
    )

    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"))
    question_set_id: Mapped[int] = mapped_column(ForeignKey("question_set.id"), nullable=True)

    question_text: Mapped[str] = mapped_column(String(300))

    # Ref: https://stackoverflow.com/a/76277425
    answer_type: Mapped[AnswerType] = mapped_column(Enum(
        *get_args(AnswerType),
        name="answer_type",
        create_constraint=True,
        validate_strings=True,
    ))




class Answer(Base):
    __tablename__ = "answer"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(), onupdate=func.CURRENT_TIMESTAMP()
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