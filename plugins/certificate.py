import requests
import shutil

def handle(event):
    if event.get('status') == 'is_signed':
      r = requests.get("https://spire.cloudfleet.io/dashboard/blimp/api/get_cert")

      if r.status_code == 200:
        with open("/opt/cloudfleet/data/shared/tls/tls_crt.pem.tmp", "w") as fh:
          fh.write(r.text)
        shutil.move("/opt/cloudfleet/data/shared/tls/tls_crt.pem.tmp", "/opt/cloudfleet/data/shared/tls/tls_crt.pem")
