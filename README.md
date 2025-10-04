# About
This is the project for my personal website [manjotbal.ca](https://manjotbal.ca). It uses
the [jinja2](https://jinja.palletsprojects.com/en/2.11.x/) templating engine to output static HTML and CSS files.

# Structure
Jinja layout files can be found in the `templates/` directory.
HTML files that extend these layout files are in the `content/` directory.
All css files are in `content/css`.

# Build
## Docker
To build and run the Docker image enter the command:
```
docker compose up --build -d
```

Go to [http://localhost:8080](http://localhost:8080) to view the website.

## Local
To build the files on your local system first set up a python virtual env:
```bash
python -m venv venv
source venv/bin/activate
```

Next install the necessary pip packages to build the site with:
```bash
python -m pip install Jinja2 PyYAML minify-html rcssmin
```

And then build with:
```bash
./build.py
```
