from pprint import pprint

from fastapi import FastAPI
from sqlalchemy import create_engine, select, update, delete
from sqlalchemy.orm import Session

from migration_0001 import run_migration as run_migration_0001
from migration_0002 import run_migration as run_migration_0002
from models import Organization, OrganizationIn, QuestionSet, Question, Answer

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
                "QuestionSet id": question.question_set_id,
                "Question text": question.question_text,
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
@app.get("/question/{id}")
@app.post("/question/{id}/update")
@app.delete("/question/{id}/delete")

@app.post("/answer/create")
@app.get("/answer/{id}")
@app.post("/answer/{id}/update")
@app.delete("/answer/{id}/delete")

@app.post("/question_set/create")
@app.get("/question_set/{id}")
@app.post("/question_set/{id}/update")
@app.delete("/question_set/{id}/delete")


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