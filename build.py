import glob
import os
from jinja2 import Environment, FileSystemLoader

template_dir = 'templates'
content_dir = 'content'
output_dir = 'output'

env = Environment(loader=FileSystemLoader([template_dir, content_dir]))

os.makedirs(output_dir, exist_ok=True)

for filename in glob.iglob(f'{content_dir}/**/*.html', recursive=True):
    # No need to have the content directory appended to filename
    # because we already set the jinja environment to search in the
    # content directory.
    filename = filename[len(content_dir) + 1:]
    template = env.get_template(filename)

    with open(f'{output_dir}/{filename}', 'w') as outfile:
        outfile.write(template.render())

