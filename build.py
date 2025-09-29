#!/usr/bin/python3

import argparse
import glob
import os
import rcssmin
import shutil
import subprocess
import yaml
from jinja2 import Environment, FileSystemLoader

# Update the build version whenever CSS or JS is updated.
# This will ensure that the user will get the latest styling
# rather than the locally cached version.
BUILD_VERSION = '1.3.3'

parser = argparse.ArgumentParser(description='Build the jinja templates into a static html site.')
parser.add_argument('--release',\
        help='Uses the appropriate variables and paths for the release version.',\
        action='store_true')
parser.add_argument('--publish',\
        help='Publish the website via rsync as USER. For example, this will publish to user@hostname. \
        Publishes to the release server if --release is specified, otherwise --host needs to also be specified.',\
        metavar='USER')
parser.add_argument('--host', help='The hostname when building or publishing to dev server. \
        e.g root@host. This must be provided if building or publishing the dev version.')
args = parser.parse_args()

template_dir = 'templates'
content_dir = 'content'
assets_dir = f'{content_dir}/assets'
css_dir = f'{content_dir}/css'
metadata_dir = 'metadata'

dev_output_dir = 'output/dev'
release_output_dir = 'output/release'

if args.release and not args.host:
    # Must be https
    hostname = 'manjotbal.ca'
    output_dir = release_output_dir
elif not args.release and args.host:
    # Make sure nginx is up and running.
    hostname = args.host
    output_dir = dev_output_dir
else:
    print('Error: One of --release or --host must be specified.')
    exit(1)

env = Environment(loader=FileSystemLoader([template_dir, content_dir]))
env.globals['build_version']=BUILD_VERSION
env.trim_blocks = True
env.lstrip_blocks = True

def format_date(date):
    format = '%b %d, %Y'
    return date.strftime(format)

env.filters['format_date'] = format_date


os.makedirs(output_dir, exist_ok=True)

metadata = dict()
yaml_files = [ f'{metadata_dir}/projects.yaml', f'{metadata_dir}/blogs.yaml' ]
for yaml_file in yaml_files:
    yaml_template = env.get_template(yaml_file)
    yaml_content = yaml.load(yaml_template.render(), yaml.Loader)

    filename = yaml_file.split('/')[-1]
    filename_key = filename.split('.')[0]
    metadata[filename_key] = yaml_content

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
        outfile.write(template.render(metadata=metadata))

# Minify CSS files
for css_file in glob.iglob(f'{css_dir}/*.css'):
    css_file = css_file[len(content_dir) + 1:]
    template = env.get_template(css_file)

    filename = css_file.split(".")[0]
    css_min = f'{filename}-min.css'
    os.makedirs(f'{output_dir}/{os.path.dirname(css_min)}', exist_ok=True)

    with open(f'{output_dir}/{css_min}', 'w') as css_min_file:
        minified = rcssmin.cssmin(template.render())
        css_min_file.write(str(minified))

shutil.copytree(assets_dir, output_dir, dirs_exist_ok=True)

print(f'Files generated in {output_dir}/')


# Use rsync to publish the contents of the release folder to the sever.
if args.publish:
    subprocess.run(['rsync', '-azP', '--usermap=*:www-data', '--groupmap=*:www-data', \
        f'{output_dir}/', f'{args.publish}@{hostname}:/var/www/manjotbal.ca'])

