# Ketch take home coding exercise

Goals of this web service are to allow for:
- Organization can create new questions
- Organization can update existing questions
- Organization can get all questions (and the corresponding answers)
- Organization can configure a question set


## Requirements to run
Docker compose is needed to run the containers for this web service. The easiest way I've found to install docker compose is through [installing Docker desktop](https://docs.docker.com/compose/install/).

To spin up the containers, `docker compose up`, and then using `CTRL+C` to quit and `docker compose down` and `docker volume prune` will bring down the containers and delete the associated volumes. So generally my routine has been to run `docker compose up`, curl the endpoints, and then use `docker compose down && docker volume prune`.

*Caveat*: I would take a quick look at your docker volumes just so that you don't unintentionally prune a volume not associated with this exercise.


## Instructions for running
1. Install Docker if needed
1. `docker compose up`
1. `curl localhost:8000/migrate`
    - this **is required** to set up the tables in the postgres database
1. `curl localhost:8000/migrate_data`
    - this **is not required**, but can help show the relationships between the various tables and skip some of the time needed to run the necessary `curl`s that would otherwise set up the objects.


## DB access (places user in psql REPL/interactive terminal)
`docker exec -it server bash -c 'PGPASSWORD=secureketchpassword789 psql -U ketchuser -h db takehome'`

## Endpoints and associated `curl` commands

### GET localhost:8000/
`curl localhost:8000/` to receive a "Hello world" response

### GET localhost:8000/migrate
`curl localhost:8000/migrate` to run the initial migration that sets up the database tables. I wanted to run things through SQLAlchemy and decided to add this route instead of running a script manually.

### GET localhost:8000/migrate_data
`curl localhost:8000/migrate_data` to run a data migration that sets up an example Organization, with an example QuestionSet with a number of Question and Answer rows tied to it, as well as one Question and related Answers that are not associated with the QuestionSet but are associated with the Organization


### POST localhost:8000/organization/create
`curl localhost:8000/organization/create --header 'Content-Type: application/json' --data '{"name": "<organization name here>"}'` to create an organization

### GET localhost:8000/organization/{id}
`curl localhost:8000/organization/{id}` to retrieve information about an organization

### GET localhost:8000/organization/{id}/all_questions
`curl localhost:8000/organization/{id}/all_questions` will retrieve a hierarchy of all the questions and their related answers in the response. The curl response is hard to read as the number of questions and related answers grows, so I used the python library `pprint` to pretty-print the output in the server logs.

### PUT localhost:8000/organization/{id}/update
```
curl --location --request PUT 'localhost:8000/organization/2/update' \
--header 'Content-Type: application/json' \
--data '{"name": "a new name for an organization"}'
```
to update an organization. The only field updateable is the name, and the only other field that changes is the "updated_at" time which reflects the most recent time this endpoint has been used.

### DELETE localhost:8000/organization/{id}/
`curl --location --request DELETE 'localhost:8000/organization/{id}'` to delete an organization.


### POST localhost:8000/question_set/create
```
curl --location 'localhost:8000/question_set/create' \
--header 'Content-Type: application/json' \
--data '{
    "name": "New question set",
    "organization_id": 1,
    "active": true,
    "question_ids": [1, 3, 4, 5]
}'
```
will create a question set. The `question_ids` parameter can be used with question ids that exist already, or it can be left blank. This is the same when creating questions, they can either be created on their own or created with a question_set_id that is non-null.

### GET localhost:8000/question_set/{id}
`curl localhost:8000/question_set/8` will retrieve information about a QuestionSet.

### GET localhost:8000/question_set/{id}/all_questions
`curl localhost:8000/question_set/8/all_questions` will retrieve detailed information about all the questions and associated answers for a question set. As with other endpoints, the information from this curl is hard to read so it is pretty printed in the container/server logs.


### PUT localhost:8000/question_set/{id}/update
```
curl --location --request PUT 'localhost:8000/question_set/8/update' \
--header 'Content-Type: application/json' \
--data '{
    "name": "A new name for question set",
    "active": true,
    "question_ids": [1, 2, 3]
}'
```
will update a question set, with the ability to change the name, the active boolean, and the associated question_ids. This will remove the question ids that are no longer listed - ie if the question in the above example had `1, 3, 4, 5` as its questions, and then this `curl` was executed, it would remove questions `4, 5` by updating those questions `question_set_id` fields, and would add the question with id `2`. Its response looks like:
```
{
    "message": "Updated QuestionSet id: 8",
    "removed_question_ids": [
        4,
        5
    ],
    "added_question_ids": [
        2
    ]
}
```
to help illustrate which question ids were added/removed from the question set.


### DELETE localhost:8000/question_set/{id}/delete
`curl --location --request DELETE 'localhost:8000/question_set/5/delete'` will delete a QuestionSet.


### POST localhost:8000/question/create
```
curl --location 'localhost:8000/question/create' \
--header 'Content-Type: application/json' \
--data '{
    "organization_id": 1,
    "question_text": "This is my first example question",
    "answer_type": "single_select"
}'
```
will create a question. The answer_type has to be `single_select` or `multiple_select`. There is an optional parameter for `question_set_id`.


### GET localhost:8000/question/{id}
`curl --location 'localhost:8000/question/1'` to get a question.


### GET localhost:8000/question/{id}/answers
`curl --location 'localhost:8000/question/{id}/answers'` to get a question with its associated answers. This can be a hard to read output so it is pretty-printed in the server logs.

### PUT localhost:8000/question/{id}/update
```
curl --location --request PUT 'localhost:8000/question/1/update' \
--header 'Content-Type: application/json' \
--data '{
    "question_text": "this is updated text",
    "question_set_id": null,
}'
```
will update a question. The `question_set_id` can be changed as well as the `question_text`.


### DELETE localhost:8000/question/{id}/delete
This will delete a question and its associated answers. I made this as an explicit design choice, and could be changed to make the `question_id` field on the `answer` table nullable.


### POST localhost:8000/answer/{id}/create
```
curl --location 'localhost:8000/answer/create' \
--header 'Content-Type: application/json' \
--data '{
    "question_id": <question_id>,
    "answer_text": "this is an answer for a question"
}'
```
will create an answer for an existing question. Questions must be created before answers can be created.


### GET localhost:8000/answer/{id}
`curl --location 'localhost:8000/answer/1'` to get an answer.


### PUT localhost:8000/answer/{id}/update
```
curl --location --request PUT 'localhost:8000/answer/1/update' \
--header 'Content-Type: application/json' \
--data '{
    "answer_text": "this is some updated answer text"
}'
```
will update an answer. The only field updateable at the moment is the `answer_text` field.


### DELETE localhost:8000/answer/{id}/delete
`curl --location --request DELETE 'localhost:8000/answer/1/delete'` will delete an answer.