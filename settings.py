import plugins.users
import plugins.certificate

channels = {
    "users": [plugins.users.handle],
    "certificate": [plugins.certificate.handle]
}

CLOUDFLEET_SECRET = os.getEnv("CLOUDFLEET_SECRET")
CLOUDFLEET_DOMAIN = os.getEnv("CLOUDFLEET_DOMAIN")
