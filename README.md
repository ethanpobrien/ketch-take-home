# Ketch take home coding exercise

Goals of this web service are to allow for:
- Organization can create new questions
- Organization can update existing questions
- Organization can get all questions (and the corresponding answers)
- Organization can configure a question set


## Requirements to run
Docker compose is needed to run the containers for this web service. The easiest way I've found to install docker compose is through [installing Docker desktop](https://docs.docker.com/compose/install/).

To spin up the containers, `docker compose up`, and then using `CTRL+C` to quit and `docker compose down` and `docker volume prune` will bring down the containers and delete the associated volumes.

*Caveat*: I would take a quick look at your docker volumes just so that you don't unintentionally prune a volume not associated with this exercise.


## DB access (places user in psql REPL/interactive terminal)
`docker exec -it server bash -c 'PGPASSWORD=secureketchpassword789 psql -U ketchuser -h db takehome'`

## Endpoints and associated `curl` commands

### localhost:8000/
`curl localhost:8000/` to receive a "Hello world" response
