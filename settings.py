import plugins.users
import plugins.certificate
import os

channels = {
    "users": [plugins.users.handle],
    "certificate": [plugins.certificate.handle]
}

CLOUDFLEET_SECRET = os.getenv("CLOUDFLEET_SECRET")
CLOUDFLEET_DOMAIN = os.getenv("CLOUDFLEET_DOMAIN")
