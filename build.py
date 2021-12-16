import argparse
import glob
import os
import rcssmin
import shutil
import socket
import subprocess
from subprocess import Popen, PIPE
from jinja2 import Environment, FileSystemLoader

# Update the build version whenever CSS or JS is updated.
# This will ensure that the user will get the latest styling
# rather than the locally cached version.
BUILD_VERSION = '1.1'

parser = argparse.ArgumentParser(description='Build the jinja templates into a static html site.')
parser.add_argument('--release',\
        help='Uses the appropriate variables and paths for the release version.',\
        action='store_true')
parser.add_argument('--publish',\
        help='Publish the website via rsync. Publishes to the release server if --release is \
        specified, otherwise the --user and --host need to also be specified.',\
        action='store_true')
parser.add_argument('--host', help='The hostname when building or publishing to dev server. \
        e.g user@host. This must be provided if only building the dev version.')
args = parser.parse_args()

template_dir = 'templates'
content_dir = 'content'
assets_dir = f'{content_dir}/assets'
dev_output_dir = 'output/dev'
release_output_dir = 'output/release'
css_dir = 'css'

if args.release:
    # Must be https
    site_url = 'https://manjotbal.ca'
    output_dir = release_output_dir
elif args.host:
    # Make sure nginx is up and running.
    site_url = f'http://{args.host}'
    output_dir = dev_output_dir
else:
    print('Error: One of --release or --host must be specified.')
    exit(1)

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

    # The path to the html needs to exist before we can open the file.
    paths = html_file.split('/')
    if len(paths) > 1:
        path_to_html = '/'.join(paths[0:-1])
        os.makedirs(f'{output_dir}/{path_to_html}', exist_ok=True)

    with open(f'{output_dir}/{html_file}', 'w') as outfile:
        outfile.write(template.render(site_url=site_url, build_version=BUILD_VERSION))

# Make sure the less npm module is installed globally.
for less_file in glob.iglob(f'{content_dir}/{css_dir}/*.less'):
    less_file = less_file[len(content_dir) + 1:]
    template = env.get_template(less_file)
    filename = less_file.split(".")[0]
    css = f'{filename}.css'
    css_min = f'{filename}-min.css'

    proc = Popen(['lessc', '-', f'{output_dir}/{css}'], stdout=PIPE, stdin=PIPE, stderr=PIPE)
    proc.communicate(input=template.render(site_url=site_url).encode())

    with open(f'{output_dir}/{css}', 'r') as css_file:
        minified = rcssmin.cssmin(css_file.read())
        with open(f'{output_dir}/{css_min}', 'w') as css_min_file:
            css_min_file.write(minified)

shutil.copytree(assets_dir, output_dir, dirs_exist_ok=True)

print(f'Files generated in {output_dir}/')


# Use rsync to publish the contents of the release folder to the sever.
if args.publish and args.release:
    subprocess.run(['rsync', '-azP', f'{output_dir}/', \
            'root@manjotbal.ca:/var/www/manjotbal.ca/html'])
    print(f'Site viewable at {site_url}')
elif args.publish and args.host:
    subprocess.run(['rsync', '-azP', f'{output_dir}/', \
            f'root@{args.host}:/var/www/manjotbal.ca'])
    print(f'Site viewable at {site_url}')
else:
    print('Error: To publish specify either --release or --host.')
    exit(1)

