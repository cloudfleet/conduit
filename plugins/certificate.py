import requests
import shutil
import sys
import settings

def handle(event):
    if event.get('status') == 'is_signed':
      sys.stdout.write("Retrieving certificate ...\n")
      r = requests.post("https://spire.cloudfleet.io/dashboard/blimp/api/get_cert", {'domain': settings.CLOUDFLEET_DOMAIN, 'secret': settings.CLOUDFLEET_SECRET})
      sys.stdout.write("Response: %s" % r.text)
      if r.status_code == 200:
        with open("/opt/cloudfleet/data/shared/tls/tls_crt.pem.tmp", "w") as fh:
          fh.write(r.json.cert)
        shutil.move("/opt/cloudfleet/data/shared/tls/tls_crt.pem.tmp", "/opt/cloudfleet/data/shared/tls/tls_crt.pem")
