from pprint import pprint

from fastapi import FastAPI
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import Session

from migration_0001 import run_migration as run_migration_0001
from migration_0002 import run_migration as run_migration_0002
from models import (
    Answer,
    AnswerIn,
    AnswerUpdateIn,
    Organization,
    OrganizationIn,
    QuestionSet,
    QuestionSetIn,
    QuestionSetUpdateIn,
    Question,
    QuestionIn,
    QuestionUpdateIn,
)

app = FastAPI()

engine = create_engine('postgresql://ketchuser:secureketchpassword789@db:5432/takehome')

@app.get("/")
async def root():
    return {"message": "Hello world"}


@app.get("/organization/all")
async def get_all_organizations():
    with Session(engine) as session:
        organizations = session.execute(
            select(Organization).order_by(Organization.id)
        ).scalars().all()
    formatted_org_info = []
    for org in organizations:
        formatted_org_info.append({
            "Id": org.id,
            "Name": org.name,
            "Created at": org.created_at,
            "Updated at": org.updated_at,
        })
    return {
        "Organizations": formatted_org_info
    }


@app.post("/organization/create")
async def create_organization(organization: OrganizationIn):
    with Session(engine) as session:
        db_org = Organization(name=organization.name)
        session.add_all([db_org])
        session.commit()
        organization = session.execute(
            select(Organization).where(Organization.name==db_org.name)
        ).scalars().all()[0]
    return {"Created resource": organization}


@app.get("/organization/{id}")
async def get_organization(id: int):
    with Session(engine) as session:
        organization = session.execute(
            select(Organization).where(Organization.id==id)
        ).scalars().all()[0]
    return {
        "Id": organization.id,
        "Name": organization.name,
        "Created at": organization.created_at,
        "Updated at": organization.updated_at,
    }

@app.put("/organization/{id}/update")
async def update_organization(id: int, organization: OrganizationIn):
    with Session(engine) as session:
        session.execute(
            update(Organization).where(Organization.id==id).values(name=organization.name)
        )
        session.commit()
        updated_org = session.execute(
            select(Organization).where(Organization.id==id)
        ).scalars().all()[0]
    return {
        "Id": updated_org.id,
        "Name": updated_org.name,
        "Created at": updated_org.created_at,
        "Updated at": updated_org.updated_at,
    }


@app.delete("/organization/{id}")
def delete_organization(id: int):
    with Session(engine) as session:
        session.execute(
            delete(Organization).where(Organization.id==id)
        )
        session.commit()
    return {"message": "Delete successful"}


@app.get("/organization/{id}/all_questions")
async def get_all_questions(id: int):
    formatted_information = {}
    with Session(engine) as session:
        organization = session.execute(
            select(Organization).where(Organization.id==id)
        ).scalars().all()[0]
        formatted_information["Organization"] = {
            "Id": organization.id,
            "Name": organization.name,
            "Created_at": organization.created_at,
        }
        questions = session.execute(
            select(Question).where(Question.organization_id==id)
        ).scalars().all()
        formatted_information["Questions"] = {}
        for question in questions:
            answers = session.execute(
                select(Answer).where(Answer.question_id==question.id)
            ).scalars().all()
            formatted_information["Questions"][f"{question.id}"] = {
                "Id": question.id,
                "Created at": question.created_at,
                "Updated at": question.updated_at,
                "QuestionSet ids": [question_set.id for question_set in question.question_set],
                "Question text": question.question_text,
                "Answer type": question.answer_type,
                "Answers": [],
            }
            for answer in answers:
                formatted_information["Questions"][f"{question.id}"]["Answers"].append({
                    "Id": answer.id,
                    "Created at": answer.created_at,
                    "Updated at": answer.updated_at,
                    "Answer text": answer.answer_text,
                })
        pprint(formatted_information)
        return formatted_information
                

@app.post("/question/create")
async def create_question(question: QuestionIn):
    with Session(engine) as session:
        db_question = Question(
            organization_id=question.organization_id,
            question_text=question.question_text,
            answer_type=question.answer_type,
        )
        if question.answer_type is None:
            return {"Error": "question.answer_type cannot be null on creation"}
        if question.question_set_id is not None:
            question_set = session.query(QuestionSet).get(question.question_set_id)
            db_question.question_set.append(question_set)
        session.add_all([db_question])
        session.commit()
        question = session.execute(
            select(Question).where(Question.question_text==db_question.question_text)
        ).scalars().all()[0]
    return {"Created resource": question}

@app.get("/question/{id}")
async def get_question(id: int):
    with Session(engine) as session:
        question = session.execute(
            select(Question).where(Question.id==id)
        ).scalars().all()[0]
    return question


@app.get("/question/{id}/answers")
async def get_question_with_answers(id: int):
    formatted_info = {}
    with Session(engine) as session:
        question = session.execute(
            select(Question).where(Question.id==id)
        ).scalars().all()[0]
        answers = session.execute(
            select(Answer).where(Answer.question_id==id)
        ).scalars().all()
        formatted_info = {
            "Id": question.id,
            "Created at": question.created_at,
            "Updated at": question.updated_at,
            "QuestionSet ids": [question_set.id for question_set in question.question_set],
            "Question text": question.question_text,
            "Answer type": question.answer_type,
            "Answers": [],
        }
        for answer in answers:
            formatted_info["Answers"].append({
                "Id": answer.id,
                "Created at": answer.created_at,
                "Updated at": answer.updated_at,
                "Answer text": answer.answer_text,
            })
    pprint(formatted_info)
    return formatted_info

@app.put("/question/{id}/update")
async def update_question(id: int, question_update: QuestionUpdateIn):
    with Session(engine) as session:
        update_stmt = update(Question).where(
            Question.id==id
        ).values(
            question_text=question_update.question_text,
        )
        session.execute(
            update_stmt
        )
        session.commit()
        updated_question = session.query(Question).get(id)
        # allowing for adding of Questions to QuestionSets from the Question update, but does not allow for removal
        #   which has to be done from the QuestionSet update route
        if question_update.question_set_id not in [question_set.id for question_set in updated_question.question_set]:
            question_set = session.query(QuestionSet).get(question_update.question_set_id)
            question_set.questions.append(updated_question)
            session.commit()
        session.refresh(updated_question)
    return updated_question

@app.delete("/question/{id}/delete")
async def delete_question(id: int):
    # delete question with answers

    with Session(engine) as session:
        session.execute(
            delete(Answer).where(Answer.question_id==id)
        )
        session.commit()
        session.execute(
            delete(Question).where(Question.id==id)
        )
        session.commit()
    return {"message": "Delete successful"}


@app.post("/answer/create")
async def create_answer(answer: AnswerIn):
    with Session(engine) as session:
        db_answer = Answer(
            question_id=answer.question_id,
            answer_text=answer.answer_text,
        )
        session.add_all([db_answer])
        session.commit()
        answer = session.execute(
            select(Answer).where(
                Answer.question_id==db_answer.question_id,
                Answer.answer_text==db_answer.answer_text
            )
        ).scalars().all()[0]
    return {"Created resource": answer}


@app.get("/answer/{id}")
async def get_answer(id: int):
    with Session(engine) as session:
        answer = session.execute(
            select(Answer).where(Answer.id==id)
        ).scalars().all()[0]
    return answer


@app.put("/answer/{id}/update")
async def update_answer(id: int, answer: AnswerUpdateIn):
    with Session(engine) as session:
        update_stmt = update(Answer).where(
            Answer.id==id
        ).values(
            answer_text=answer.answer_text,
        )
        session.execute(
            update_stmt
        )
        session.commit()
        updated_answer = session.execute(
            select(Answer).where(Answer.id==id)
        ).scalars().all()[0]
    return updated_answer 


@app.delete("/answer/{id}/delete")
async def delete_answer(id: int):
    with Session(engine) as session:
        session.execute(
            delete(Answer).where(Answer.id==id)
        )
        session.commit()
    return {"message": "Delete successful"}

@app.post("/question_set/create")
async def create_question_set(question_set_in: QuestionSetIn):
    with Session(engine) as session:
        # set other QuestionSets to inactive
        if question_set_in.active:
            session.execute(
                update(QuestionSet).where(QuestionSet.active==True).values(active=False)
            )
            session.commit()
        # create QuestionSet
        db_question_set = QuestionSet(
            organization_id=question_set_in.organization_id,
            name=question_set_in.name,
            active=question_set_in.active,
        )
        session.add_all([db_question_set])
        session.commit()
        session.refresh(db_question_set)
        for question_id in question_set_in.question_ids:
            question = session.query(Question).get(question_id)
            db_question_set.questions.append(question)
            session.commit()
        return {"message": f"Created QuestionSet with Id {db_question_set.id} and added Question Ids {question_set_in.question_ids} to the QuestionSet"}

@app.get("/question_set/{id}")
async def get_question_set(id: int):
    with Session(engine) as session:
        question_set = session.execute(
            select(QuestionSet).where(QuestionSet.id==id)
        ).scalars().all()[0]
    return question_set

@app.get("/question_set/{id}/all_questions")
async def get_question_set_with_questions(id: int):
    formatted_information = {}
    with Session(engine) as session:
        question_set = session.execute(
            select(QuestionSet).where(QuestionSet.id==id)
        ).scalars().all()[0]
        formatted_information["QuestionSet"] = {
            "Id": question_set.id,
            "Name": question_set.name,
            "Created_at": question_set.created_at,
            "Updated_at": question_set.updated_at,
        }
        questions = question_set.questions
        formatted_information["Questions"] = {}
        for question in questions:
            answers = session.execute(
                select(Answer).where(Answer.question_id==question.id)
            ).scalars().all()
            formatted_information["Questions"][f"{question.id}"] = {
                "Id": question.id,
                "Created at": question.created_at,
                "Updated at": question.updated_at,
                "QuestionSet ids": [question_set.id for question_set in question.question_set],
                "Question text": question.question_text,
                "Answer type": question.answer_type,
                "Answers": [],
            }
            for answer in answers:
                formatted_information["Questions"][f"{question.id}"]["Answers"].append({
                    "Id": answer.id,
                    "Created at": answer.created_at,
                    "Updated at": answer.updated_at,
                    "Answer text": answer.answer_text,
                })
    pprint(formatted_information)
    return formatted_information

@app.put("/question_set/{id}/update")
async def update_question_set(id: int, question_set_in: QuestionSetUpdateIn):
    with Session(engine) as session:
        question_set = session.query(QuestionSet).get(id)
        # if change is enabling a question set, disable other active question set
        set_to_active = False
        if question_set_in.active == True and question_set.active != True:
            session.execute(
                update(QuestionSet).where(QuestionSet.active==True).values(active=False)
            )
            session.commit()
            set_to_active = True
        session.execute(
            update(QuestionSet).where(QuestionSet.id==id).values(
                name=question_set.name,
                active=question_set_in.active,
            )
        )
        session.commit()
        session.refresh(question_set)
        active_question_ids = [question.id for question in question_set.questions]
        new_question_ids = [question_id for question_id in question_set_in.question_ids if question_id not in active_question_ids]
        disable_question_ids = [question_id for question_id in active_question_ids if question_id not in question_set_in.question_ids]

        for question_id in new_question_ids:
            # go through net new question_ids and add them to the question_set
            question = session.query(Question).get(question_id)
            question_set.questions.append(question)
            session.commit()

        for question_id in disable_question_ids:
            # go through question_ids that were active before this update came in
            #   and disconnect them from the question_set
            question = session.query(Question).get(question_id)
            question_set.questions.remove(question)
            session.commit()
    return {
        "message": f"Updated QuestionSet id: {id}",
        "removed_question_ids": disable_question_ids,
        "added_question_ids": new_question_ids,
        "set_to_active_question_set": set_to_active,
    }

@app.delete("/question_set/{id}/delete")
async def delete_question_set(id: int):
    with Session(engine) as session:
        session.execute(
            delete(QuestionSet).where(QuestionSet.id==id)
        )
        session.commit()
    return {"message": "Delete successful"}


########################################
# Migration related endpoints in lieu of
#   a more elegant solution
########################################

@app.get("/migrate")
async def migrate():
    run_migration_0001()
    return {"message": "Migration complete! Ran migration_0001.py"}

@app.get("/migrate_data")
async def migrate_data():
    run_migration_0002()
    return {"message": "Migration complete! Ran migration_0002.py"}