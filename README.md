# wine predictor app

This is an application that a RESTapi request containing the ID of a wine and some real time measurements, gets other relevant features from a database and uses them to get a result from a model. This project is an introduction in ML-ops, just to tests out different ideas and patterns.

the project uses rabbitMQ for handling requests. it puts requests in a queue, which are then cared for by workers, that work independently of each other, therefor they can be cloned as many times as one might want. the app has a simple UI on localhost port 3000 by default (can be changed in the .env file).

## how to run

1. create a .env file and copy everything from .env.example. if you want to download a different model, you must also add DATABRICKS_HOST and DATABRICKS_TOKEN in the .env file.
2. run `docker compose -f 'docker-compose.yml' up -d --build`. in case the app does not show, restart the broker_container container.