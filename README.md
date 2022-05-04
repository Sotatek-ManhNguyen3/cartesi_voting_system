This example shows a simple book catalog DApp based on SQLite database running inside the cartesi machine.

## How this example works
User will send an input as a sql query to get, insert, update or delete books info, The cartesi rollups will receive input and return the result.

- If the query is insert, update or delete, the result will be "success"
- If there are any errors, the result will be a string with description of the error. Example: "EXCEPTION: syntax error"
- If the query is get, the result will be the data from database

The books table contain 3 column:

| Column name | Data type |
|-------------|-----------|
| id          | integer   |
| name        | string    |
| quantity    | integer   |

## Building the environment

To run the sqlite poc example, clone the repository as follows:

```shell
$ git clone git@github.com:Sotatek-ManhNguyen3/cartesi_sqlite_poc.git
```

Then, build the back-end for the voting example:

```shell
$ make machine
```

## Running the environment

In order to start the containers in production mode, simply run:

```shell
$ docker-compose up --build
```

_Note:_ If you decide to use [Docker Compose V2](https://docs.docker.com/compose/cli-command/), make sure you set the [compatibility flag](https://docs.docker.com/compose/cli-command-compatibility/) when executing the command (e.g., `docker compose --compatibility up`).

Allow some time for the infrastructure to be ready.
How much will depend on your system, but after some time showing the error `"concurrent call in session"`, eventually the container logs will repeatedly show the following:

```shell
server_manager_1      | Received GetVersion
server_manager_1      | Received GetStatus
server_manager_1      |   default_rollups_id
server_manager_1      | Received GetSessionStatus for session default_rollups_id
server_manager_1      |   0
server_manager_1      | Received GetEpochStatus for session default_rollups_id epoch 0
```

To stop the containers, first end the process with `Ctrl + C`.
Then, remove the containers and associated volumes by executing:

```shell
$ docker-compose down -v
```

## Interacting with the application

With the infrastructure in place, go to a separate terminal window and send an input as follows:

```shell
$ docker exec cartesi_voting_system_hardhat_1 npx hardhat --network localhost voting:addInput --input "0x7B22616374696F6E223A20224C4953545F414C4C227D"
```
This input means `select * from books`

You can replace this query by another query to retrieve the expected result. Such as:

`INSERT INTO books VALUES (2, "Book 2", 30)`

`SELECT * FROM books WHERE name = "Book 2"`

The input will have been accepted when you receive a response similar to the following one:

```shell
Added input '0x73656C656374202A2066726F6D20626F6F6B73' to epoch '0' (timestamp: 1646377281, signer: 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266, tx: 0xfac214be3290c7d3e856e915707a4c97538911b676eaa76e79c84133c2875d9e)
```

In order to verify the notices generated by your inputs, run the command:

```shell
$ curl http://localhost:4000/graphql -H 'Content-Type: application/json' -d '{ "query" : "query getNotice { GetNotice( query: { session_id: \"default_rollups_id\", epoch_index: \"0\", input_index: \"0\" } ) { session_id epoch_index input_index notice_index payload } }" }'
```

The response should be something like this:

```shell
{"data":{"GetNotice":[{"session_id":"default_rollups_id","epoch_index":"0","input_index":"0","notice_index":"0","payload":"5b5d"}]}}
```
The data in payload is `[]`, it means there is no record of books in the database yet
