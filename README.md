# JSON Fixer for Python

A Python library that tries to fix broken JSON strings. This is a Python port of the JavaScript
library [jsonrepair](https://github.com/josdejong/jsonrepair).

## Description

This Python package attempts to repair malformed JSON strings. It is designed to handle common cases of bad JSON, as
follows:

- Add missing quotes around keys
- Add missing escape characters
- Add missing commas
- Add missing closing brackets
- Replace single quotes with double quotes
- Replace special quote characters like “...” with regular double quotes
- Replace special white space characters with regular spaces
- Replace Python constants None, True, and False with null, true, and false
- Strip trailing commas
- Strip comments like /* ... */ and // ...
- Strip JSONP notation like callback({ ... })
- Strip escape characters from an escaped string like {"stringified": "content"}
- Strip MongoDB data types like NumberLong(2) and ISODate("2012-12-19T06:01:17.171Z")
- Concatenate strings like "long text" + "more text on next line"
- Turn newline-delimited JSON into a valid JSON array, for example:
  { "id": 1, "name": "John" }
  { "id": 2, "name": "Sarah" }

## Installation

### Clone the Repository

```shell
git clone git@github.com:aleksandrphilippov/json-fixer.git
cd json-fixer
```

### Local Installation

After cloning the repository, navigate to the project directory and run the example script:

```shell
python example.py
```

### Docker Installation

If you have Docker and Docker Compose installed, you can use the provided `Dockerfile` and `docker-compose.yml` to build
and run the application in a Docker container. This avoids the need to install Python and other dependencies on your
local machine.

Build the Docker image:

```shell
docker compose build
```

Run the application in a Docker container:

```shell
docker compose up -d
```

This will start the `json_fixer` service as defined in your `docker-compose.yml` file. The application will run using
the command specified in the `CMD` directive of your `Dockerfile` (in this case, `python example.py`).

To stop the Docker container:

```shell
docker compose down
```

To remove the Docker image:

```shell
docker rmi json-fixer_json_fixer
```

### Makefile Commands

Another option for managing the project is to use the `Makefile`:

Build the Docker containers:

```shell
make build
```

Start the application:

```shell
make start
```

Stop the application:

```shell
make stop
```

Tail the logs for the application:

```shell
make logs
```

Run tests:

```shell
make test
```

## Usage

To use `json_fixer` in your Python script, you first need to import the module and then call the `fix` function with
your malformed JSON string as the argument. Here is an example:

```python
from json_fixer import fix_json

broken_json = '{`name`: "John", age: 30, "city": New York}'
fixed_json = fix_json(broken_json)
print(fixed_json)
```

This will output:

```json
{"name": "John", "age": 30, "city": "New York"}
```

## Testing

To run the tests for this project, navigate to the project directory in your terminal and run:

```shell
python -m unittest json_fixer.fixer_test
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this
project.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/YourFeature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin feature/YourFeature`)
5. Create a new Pull Request

## Acknowledgements

This project is a Python port of the [jsonrepair](https://github.com/josdejong/jsonrepair) JavaScript library by Jos de
Jong. Huge thanks to him for the original implementation.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
