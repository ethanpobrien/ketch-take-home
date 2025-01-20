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

### PUT localhost:8000/organization/{id}/update
`curl --location --request PUT 'localhost:8000/organization/1/update' --header 'Content-Type: application/json' --data '{"name": "<a new name for an organization>"}'` to update an organization. The only field updateable is the name, and the only other field that changes is the "updated_at" time which reflects the most recent time this endpoint has been used.

### DELETE localhost:8000/organization/{id}/
`curl --location --request DELETE 'localhost:8000/organization/{id}'` to delete an organization.