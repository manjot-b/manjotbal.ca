#!/usr/bin/env python

import argparse
import glob
import gzip
import os
import minify_html
import rcssmin
import shutil
import yaml
from jinja2 import Environment, FileSystemLoader

# Update the build version whenever CSS or JS is updated.
# This will ensure that the user will get the latest styling
# rather than the locally cached version.
BUILD_VERSION = '2'

parser = argparse.ArgumentParser(description='Build the jinja templates into a static html site.')
parser.add_argument('--no-min',\
        help='Do not minify the html and css files. Used for debugging.',\
        action='store_true')
args = parser.parse_args()

template_dir = 'templates'
content_dir = 'content'
assets_dir = f'{content_dir}/assets'
css_dir = f'{content_dir}/css'
metadata_dir = 'metadata'
output_dir = 'output'

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
    html_file_path = html_file[len(content_dir) + 1:]
    template = env.get_template(html_file_path)

    # The path to the html needs to exist before we can open the file.
    paths = html_file_path.split('/')
    if len(paths) > 1:
        path_to_html = '/'.join(paths[0:-1])
        os.makedirs(f'{output_dir}/{path_to_html}', exist_ok=True)

    rendered_html = template.render(metadata=metadata)
    with open(f'{output_dir}/{html_file_path}', 'w') as html_file:
        if args.no_min:
            html_file.write(rendered_html)
        else:
            html_min_file = minify_html.minify(rendered_html)
            html_file.write(html_min_file)

    with gzip.open(f'{output_dir}/{html_file_path}.gz', 'wb') as html_gzip_file:
        html_gzip_file.write(rendered_html.encode('utf-8'))

# Minify CSS files
for css_file in glob.iglob(f'{css_dir}/*.css'):
    css_file = css_file[len(content_dir) + 1:]
    template = env.get_template(css_file)

    filename = css_file.split(".")[0]
    css_min = f'{filename}-min.css'
    os.makedirs(f'{output_dir}/{os.path.dirname(css_min)}', exist_ok=True)

    rendered_css = template.render()
    with open(f'{output_dir}/{css_min}', 'w') as css_file:
        if args.no_min:
            css_file.write(rendered_css)
        else:
            css_min_file = rcssmin.cssmin(rendered_css)
            css_file.write(str(css_min_file))

    with gzip.open(f'{output_dir}/{css_min}.gz', 'wb') as css_gzip_file:
        css_gzip_file.write(rendered_css.encode('utf-8'))

shutil.copytree(assets_dir, output_dir, dirs_exist_ok=True)

print(f'Files generated in {output_dir}/')

