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
    - this **is not required**, but it is suggested to help show the relationships between the various tables and skip some of the time needed to run the necessary `curl`s that would otherwise set up the objects.
1. `curl localhost:8000/organization/1/all_questions`
    - this will print out all of the questions of the organization, and will pretty-print the information in the docker container logs for easier readability.
1. `curl localhost:8000/question_set/1/all_questions`
    - this will return a similar result, but with one less question as only 4 questions are associated with the QuestionSet. The server logs show the same formatted output as the curl is hard to read.

If you would like to create your own Organization and go from there, here are the commands you will need:
1. `curl localhost:8000/organization/create --header 'Content-Type: application/json' --data '{"name": "New Organization"}'`
    - save the Id from this output, in my case, `2`.
1. Use the following curl command to create a QuestionSet, using the Id from the last output as the input for the `organization_id` parameter:
    ```
    curl --location 'localhost:8000/question_set/create' \
    --header 'Content-Type: application/json' \
    --data '{
        "name": "My question set",
        "organization_id": 2,
        "active": true,
        "question_ids": []
    }'
    ```
    - save the Id from this output as well, which was again `2`.
    - we will use this to create Questions associated with this QuestionSet.
1. Then create a Question associated with the QuestionSet:
    ```
    curl --location 'localhost:8000/question/create' \
    --header 'Content-Type: application/json' \
    --data '{
        "organization_id": 2,
        "question_text": "This is my first example question",
        "answer_type": "single_select",
        "question_set_id": 2
    }'
    ```
    Which has a response that looks like:
    ```
    {"Created resource":{"question_text":"This is my first example question","organization_id":2,"question_set_id":2,"answer_type":"single_select","id":6,"updated_at":"2025-01-21T01:48:18.305053","created_at":"2025-01-21T01:48:18.305053"}}
    ```
    - save the Id from this as well, as we'll need the Id of this question to create one or more Answers for the Question.
1. And create an associated Answer for this Question, using the output "id" from the response to the last `curl` as an input for "question_id":
    ```
    curl --location 'localhost:8000/answer/create' \
    --header 'Content-Type: application/json' \
    --data '{
        "question_id": 6,
        "answer_text": "this is an answer for a question"
    }'
    ```
1. Now you should be able to curl the `question_set/{id}/all_questions` endpoint and see the objects created in the last 4 commands:
    ```
    curl localhost:8000/question_set/2/all_questions
    ```
    and the output for me, from the docker container, looks like:
    ```
    server  | INFO:     172.18.0.1:59260 - "POST /answer/create HTTP/1.1" 200 OK
    server  | {'QuestionSet': {'Created_at': datetime.datetime(2025, 1, 21, 1, 44, 28, 578875),
    server  |                  'Id': 2,
    server  |                  'Name': 'My question set',
    server  |                  'Updated_at': datetime.datetime(2025, 1, 21, 1, 44, 28, 578875)},
    server  |  'Questions': {'6': {'Answer type': 'single_select',
    server  |                      'Answers': [{'Answer text': 'this is an answer for a '
    server  |                                                  'question',
    server  |                                   'Created at': datetime.datetime(2025, 1, 21, 1, 53, 31, 409907),
    server  |                                   'Id': 21,
    server  |                                   'Updated at': datetime.datetime(2025, 1, 21, 1, 53, 31, 409907)}],
    server  |                      'Created at': datetime.datetime(2025, 1, 21, 1, 48, 18, 305053),
    server  |                      'Id': 6,
    server  |                      'Question text': 'This is my first example question',
    server  |                      'QuestionSet id': 2,
    server  |                      'Updated at': datetime.datetime(2025, 1, 21, 1, 48, 18, 305053)}}} 
    ```
1. You can continue to create Questions and Answers, and keep adding them to the QuestionSet on Question creation. However, if you have a number of Questions and you want to associate them with the QuestionSet after creation, you can do so with the update endpoint for the QuestionSet:
    ```
    curl --location --request PUT 'localhost:8000/question_set/2/update' \
    --header 'Content-Type: application/json' \
    --data '{
        "name": "A new name for question set",
        "active": true,
        "question_ids": [1, 2, 3, 6]
    }'
    ```
    This endpoint expects the question_ids to be a full description of the intended Questions that are to be associated with the QuestionSet, and its response describes any additions or deletions made as a result of this API call:
    ```
    {
        "message":"Updated QuestionSet id: 2",
        "removed_question_ids":[],
        "added_question_ids":[1,2,3]
    }
    ```
    and if I run the same command immediately after, it will respond with:
    ```
    {
        "message":"Updated QuestionSet id: 2",
        "removed_question_ids":[],
        "added_question_ids":[]
    }
    ```
    because no change has occurred with respect to the associated Question ids.

1. Questions can be updated at the `question/{id}/update` endpoint:
    ```
    curl --location --request PUT 'localhost:8000/question/1/update' \
    --header 'Content-Type: application/json' \
    --data '{
        "question_text": "this is updated text",
        "question_set_id": null,
    }'
    ```
    and the `question_set_id` will need to be non-null if an existing link to a QuestionSet is intended to stay in place.


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


## Final thoughts
I went through this project with the idea of ultimately having a table called `UserAnswer` that would keep track of how users had filled out QuestionSets (if organizations used them) or just Questions offered by an organization. This UserAnswer table would track which Question and Answer(s) were selected by the user, and would provide validation to reinforce the `answer_type` field that is set on Questions.
I tried to put as much CRUD functionality into this as I could, and to keep the documentation up to date as well. I think there are a couple endpoints that are either not implemented for the current tables or are not fleshed out fully.
There are also a number of changes I would like to make that would make for a better web service:
1. Better handling of errors, propagating server side errors through the API to indicate if Ids do not exist in tables, etc.
    1. right now everything just shows as an Internal Server Error.
2. Authentication so that the API user isn't a superuser, but is restricted to their organization only.
    1. This would require authentication which I thought was out of scope for the current project but would be a hard requirement if this were a proof of concept for a customer.
3. A better fleshed out migration system for the database tables
    1. right now there is a very basic migration system, with a single table setup migration and a data seeding migration, and as I have not used SQLAlchemy before I am not sure how this pattern would scale but I think it would not scale well.
    1. [Alembic](https://alembic.sqlalchemy.org/en/latest/autogenerate.html) seems like the natural choice for a SQLAlchemy project.