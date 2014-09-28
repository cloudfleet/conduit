import plugins.users
from jinja2 import Environment, PackageLoader

channels = {
    "users": [plugins.users.handle]
}

MAILPILE_DOCKER_IMAGE = "cloudfleet/blimp-mailpile"

PORT_ASSIGNMENT_FILE_LOCATION = "/opt/cloudfleet/conf/port-assignments.json"

NGINX_CONFIG_DIR = "/opt/cloudfleet/conf/nginx"

JINJA_ENV = Environment(loader=PackageLoader('conduit', 'templates'))
