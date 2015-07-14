import plugins.users
import plugins.certificate
import os

channels = {
    "users": [plugins.users.handle],
    "certificate": [plugins.certificate.handle]
}

CLOUDFLEET_SECRET = os.get_env("CLOUDFLEET_SECRET")
CLOUDFLEET_DOMAIN = os.get_env("CLOUDFLEET_DOMAIN")
