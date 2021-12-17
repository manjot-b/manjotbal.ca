# About
This is the project for my personal website [manjotbal.ca](https://manjotbal.ca). It uses
the [jinja2](https://jinja.palletsprojects.com/en/2.11.x/) templating engine to output static HTML and CSS files.

# Structure
Jinja layout files can be found in the `templates/` directory.
HTML files that extend these layout files are in the `content/` directory.
All Less files are in `content/css` and when generated will be placed in `output/<mode>/css/`.

# Usage
To generate the dev files to be run on a local (vm) nginx webserver enter
```
python3 build.py --host <host-address>
```
To publish the contents of this directory to a server of your choosing.
```
python3 build.py --publish --host <host-address>
```

To generate the release files add the `--release` switch,
```
python3 build.py --release
```
The generated files can be found in `output/release/`.

To publish to the remote server (requries SSH keys on server) enter
```
python3 build.py --release --publish
```
