from subprocess import call

def handle(event):
    if event.get('action') == 'create' and event.get('username'):
        call(['/opt/cloudfleet/engineroom/bin/start-missing-user-containers.sh'])
    else:
        print str(event)
