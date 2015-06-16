import os.path, settings, json, subprocess, requests, time
import random
from subprocess import call


def create_random_id():
    number = random.randint(2**63, 2**64)

    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'

    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]


def setup_mailpile(domain, password, host, username):

    session = requests.session()


    time.sleep(10.1)
    print "\n================"
    print "Setting up language"
    setup_lang_data = {
        'language': 'en_US',
        'advance': True,
    }
    r = session.post("https://%s/mailpile/%s/setup/welcome/" % (host, username), data=setup_lang_data, allow_redirects=False)
    print r.text
    time.sleep(.1)
    print "\n================"
    print "Setting up passphrase"
    setup_crypto_data = {
        'passphrase': password,
        'passphrase_confirm': password,
        'choose_key': '!CREATE',
    }
    r = session.post("https://%s/mailpile/%s/setup/crypto/as/json" % (host, username), data=setup_crypto_data)
    print r.text
    time.sleep(.1)
    print "\n================ "
    print "Setting up smtp server"
    route_id = create_random_id()
    setup_route_data = {
        "name": "CloudFleet Route",
        "username": "",
        "password": "",
        "host": "doveshed",
        "port": "1025",
        "protocol": "smtp",
        "_section": "routes.%s" % route_id
    }
    r = session.post("https://%s/mailpile/%s/api/0/settings/set/" % (host, username), data=setup_route_data)
    print r.text
    time.sleep(.1)
    print "\n================ "
    print "Setting up profile"
    setup_profile_data = {
        "name": username,
        "email": "%s@%s" % (username, domain),
        "pass": "25", # TODO check what this is for
        "route_id": route_id,
        "note": "CloudFleet Default Profile"
    }
    r = session.post("https://%s/mailpile/%s/api/0/setup/profiles/" % (host, username),
                     data=setup_profile_data)
    print r.text
    time.sleep(1.1)


    print "\n================ "
    print "Getting Tags"


    time.sleep(.1)
    r = session.get("https://%s/mailpile/%s/tags/as.json" % (host, username))

    print r.text

    tags_dict = r.json()

    print tags_dict

    single_tasks_list = [tag for tag in tags_dict["result"]["tags"] if tag["type"] == "inbox"]
    inbox_tag_id = single_tasks_list[0]["tid"]

    print "\n================ "
    print "Setting up maildir"
    source_id = create_random_id()
    setup_source_data = {
        "protocol": "maildir",
        "discovery.paths[]": "/opt/cloudfleet/Mails",
        "discovery.local_copy": "false",
        "discovery.policy": "read",
        "discovery.apply_tags": [inbox_tag_id],
        "_section": "sources.%s" % source_id
    }
    r = session.post("https://%s/mailpile/%s/api/0/settings/set/" % (host, username), data=setup_source_data)
    print r.text

    print "\n================ "
    print "Completing setup"
    complete_setup_data = {
        "web.setup_complete": True,
    }
    r = session.post("https://%s/mailpile/%s/api/0/settings/set/" % (host, username), data=complete_setup_data)
    print r.text



def handle(event):
    if event.get('action') == 'create' and event.get('username'):

        username = event.get('username')
        password = event.get('password')
        domain = event.get('domain')

        call(['/opt/cloudfleet/engineroom/bin/upgrade-containers.sh'])

        setup_mailpile(domain, password, "blimp." + domain, username)


    else:
        print str(event)
