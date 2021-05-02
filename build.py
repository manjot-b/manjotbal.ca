import argparse
import glob
import os
import shutil
from jinja2 import Environment, FileSystemLoader

parser = argparse.ArgumentParser(description='Build the jinja templates into a static html site.')
parser.add_argument('--release',\
        help='Uses the appropriate variables and paths for the release version.',\
        action='store_true')
args = parser.parse_args()

template_dir = 'templates'
content_dir = 'content'
static_dir = f'{content_dir}/static'
output_dir = 'output'

if args.release:
    # TO-DO: change to https when available.
    site_url = "http://manjotbal.ca"
else:
    site_url = f'{os.getcwd()}/{output_dir}'

env = Environment(loader=FileSystemLoader([template_dir, content_dir]))
env.trim_blocks = True
env.lstrip_blocks = True

os.makedirs(output_dir, exist_ok=True)

for filename in glob.iglob(f'{content_dir}/**/*.html', recursive=True):
    # No need to have the content directory appended to filename
    # because we already set the jinja environment to search in the
    # content directory.
    filename = filename[len(content_dir) + 1:]
    template = env.get_template(filename)

    with open(f'{output_dir}/{filename}', 'w') as outfile:
        outfile.write(template.render(site_url=site_url))

shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
