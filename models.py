from datetime import datetime
from typing import Literal
from typing import get_args

from sqlalchemy import String, ForeignKey, Enum, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


AnswerType = Literal["single_select", "multiple_select"]

# timestamp = Annotated[
#     datetime,
#     mapped_column(nullable=False, server_default=func.CURRENT_TIMESTAMP)
# ]


class Base(DeclarativeBase):
    pass


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(primary_key=True)
    org_name: Mapped[str] = mapped_column(String(60))
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )


class Question(Base):
    __tablename__ = "question"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_text: Mapped[str] = mapped_column(String(300))
    organization_id: Mapped[int] = mapped_column(ForeignKey("organization.id"))
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(), onupdate=func.CURRENT_TIMESTAMP()
    )

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
    answer_text: Mapped[str] = mapped_column(String(100))
    question_id: Mapped[int] = mapped_column(ForeignKey("question.id"))
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )
    updated_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP(), onupdate=func.CURRENT_TIMESTAMP()
    )


class Migration(Base):
    __tablename__ = "migration"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    migrated: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(
        insert_default=func.CURRENT_TIMESTAMP()
    )