from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Organization, Question, Answer, QuestionSet, Migration

def run_migration():
    """
    This is a data migration for prepopulating an example organization
        with example questions, answers, and an example questionset
    """
    engine = create_engine('postgresql://ketchuser:secureketchpassword789@db:5432/takehome')

    # check if migration has run already
    with Session(engine) as session:
        migration_select_stmt = select(Migration).where(Migration.name=="migration_0002")
        migration_result = session.execute(migration_select_stmt)
        if len(migration_result.scalars().all()) > 0:
            migration_0002 = migration_result.scalars().all()[0]
            if migration_0002.migrated is True:
                print('Migration has already ran, skipping')
                return True
        else:
            print('Migration not recorded, will migrate and save migration_0002 as ran')
    
    with Session(engine) as session:
        # create Organization
        org = Organization(name="Example Organization")
        session.add_all([org])
        session.commit()

        # fetch Organization to get id
        org = session.scalars(
            select(Organization).where(Organization.name=="Example Organization")
        ).all()[0]

        # create QuestionSet
        question_set = QuestionSet(
            name="Example QuestionSet",
            active=True,
            organization_id=org.id
        )
        session.add_all([question_set])
        session.commit()

        # fetch QuestionSet
        question_set = session.scalars(
            select(QuestionSet).where(QuestionSet.name=="Example QuestionSet")
        ).all()[0]

        # create questions
        question_01 = Question(
            organization_id=org.id,
            # question_set_id=question_set.id,
            question_text="First example question text?",
            answer_type="single_select",
        )
        question_02 = Question(
            organization_id=org.id,
            # question_set_id=question_set.id,
            question_text="Second example question text?",
            answer_type="multiple_select",
        )
        question_03 = Question(
            organization_id=org.id,
            # question_set_id=question_set.id,
            question_text="Third example question text?",
            answer_type="single_select",
        )
        question_04 = Question(
            organization_id=org.id,
            # question_set_id=question_set.id,
            question_text="Fourth example question text?",
            answer_type="multiple_select",
        )
        question_05 = Question(
            organization_id=org.id,
            question_text="Fifth example question text, not associated with a QuestionSet?",
            answer_type="single_select",
        )

        session.add_all([
            question_01,
            question_02,
            question_03,
            question_04,
            question_05,
        ])
        session.commit()
        question_set.questions.append(question_01)
        question_set.questions.append(question_02)
        question_set.questions.append(question_03)
        question_set.questions.append(question_04)
        session.commit()

        # fetch Questions
        questions = session.scalars(
            select(Question).where(Question.organization_id==org.id)
        ).all()
        question_ids = [question.id for question in questions]

        # create Answer entries for each Question
        for question_id in question_ids:
            answer_01 = Answer(
                question_id=question_id,
                answer_text=f"Answer 01 for question_id {question_id}",
            )
            answer_02 = Answer(
                question_id=question_id,
                answer_text=f"Answer 02 for question_id {question_id}",
            )
            answer_03 = Answer(
                question_id=question_id,
                answer_text=f"Answer 03 for question_id {question_id}",
            )
            answer_04 = Answer(
                question_id=question_id,
                answer_text=f"Answer 04 for question_id {question_id}",
            )
            session.add_all([
                answer_01,
                answer_02,
                answer_03,
                answer_04,
            ])
            session.commit()

    # mark migration as migrated
    with Session(engine) as session:
        migration_0002 = Migration(
            name="migration_0002",
            migrated=True,
        )
        session.add_all([migration_0002])
        session.commit()
    
    return True