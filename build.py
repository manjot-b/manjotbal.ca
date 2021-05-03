import argparse
import glob
import os
import shutil
from subprocess import Popen, PIPE
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
css_dir = 'css'

if args.release:
    # TO-DO: change to https when available.
    site_url = 'http://manjotbal.ca'
else:
    site_url = f'{os.getcwd()}/{output_dir}'

env = Environment(loader=FileSystemLoader([template_dir, content_dir]))
env.trim_blocks = True
env.lstrip_blocks = True

os.makedirs(output_dir, exist_ok=True)

for html_file in glob.iglob(f'{content_dir}/**/*.html', recursive=True):
    # No need to have the content directory appended to filename
    # because we already set the jinja environment to search in the
    # content directory.
    html_file = html_file[len(content_dir) + 1:]
    template = env.get_template(html_file)

    with open(f'{output_dir}/{html_file}', 'w') as outfile:
        outfile.write(template.render(site_url=site_url))

# Make sure the less npm module is installed globally.
for less_file in glob.iglob(f'{content_dir}/{css_dir}/*.less'):
    less_file = less_file[len(content_dir) + 1:]
    template = env.get_template(less_file)
    css = f'{less_file.split(".")[0]}.css'

    proc = Popen(['lessc', '-', f'{output_dir}/{css}'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    proc.communicate(input=template.render(site_url=site_url).encode())

shutil.copytree(static_dir, output_dir, dirs_exist_ok=True)
