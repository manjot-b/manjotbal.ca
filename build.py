import argparse
import glob
import os
import shutil
import socket
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
dev_output_dir = 'output/dev'
release_output_dir = 'output/release'
css_dir = 'css'

if args.release:
    # Must be https
    site_url = 'https://manjotbal.ca'
    output_dir = release_output_dir
else:
    # Hack to get the local ip address.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(('0.0.0.1', 1))
        ip = sock.getsockname()[0]
    except:
        print('Error while trying to get local ip')
    finally:
        sock.close()

    # Make sure nginx is up and running.
    site_url = f'http://{ip}'
    output_dir = dev_output_dir

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

print(f'Files generated in {output_dir}/')
print(f'Site viewable at {site_url}')
