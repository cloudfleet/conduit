import docker, os.path, settings, json, subprocess, requests, time
import random


def create_random_id():
    number = random.randint(2**63, 2**64)

    alphabet = '0123456789abcdefghijklmnopqrstuvwxyz'

    base36 = ''
    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36 or alphabet[0]


def setup_mailpile(domain, password, port, username):

    session = requests.session()


    time.sleep(.1)
    print "\n================"
    print "Setting up language"
    setup_lang_data = {
        'language': 'en_US',
        'advance': True,
    }
    r = session.post("http://localhost:%s/mailpile/%s/setup/welcome/" % (port, username), data=setup_lang_data, allow_redirects=False)
    print r.text
    time.sleep(.1)
    print "\n================"
    print "Setting up passphrase"
    setup_crypto_data = {
        'passphrase': password,
        'passphrase_confirm': password,
        'choose_key': '!CREATE',
    }
    r = session.post("http://localhost:%s/mailpile/%s/setup/crypto/as/json" % (port, username), data=setup_crypto_data)
    print r.text
    time.sleep(.1)
    print "\n================ "
    print "Setting up smtp server"
    route_id = create_random_id()
    setup_route_data = {
        "name": "CloudFleet Route",
        "username": "",
        "password": "",
        "host": "blimp-docker",
        "port": "25",
        "protocol": "smtp",
        "_section": "routes.%s" % route_id
    }
    r = session.post("http://localhost:%s/mailpile/%s/api/0/settings/set/" % (port, username), data=setup_route_data)
    print r.text
    time.sleep(.1)
    print "\n================ "
    print "Setting up profile"
    setup_profile_data = {
        "name": username,
        "email": "%s@%s" % (username, domain),
        "pass": "25",
        "route_id": route_id,
        "note": "CloudFleet Default Profile"
    }
    r = session.post("http://localhost:%s/mailpile/%s/api/0/setup/profiles/" % (port, username),
                     data=setup_profile_data)
    print r.text
    time.sleep(.1)
    print "\n================ "
    print "Setting up maildir"
    source_id = create_random_id()
    setup_source_data = {
        "protocol": "maildir",
        "discovery.paths[]": "/opt/cloudfleet/Mails",
        "discovery.local_copy": "false",
        "_section": "sources.%s" % source_id
    }
    r = session.post("http://localhost:%s/mailpile/%s/api/0/settings/set/" % (port, username), data=setup_source_data)
    print r.text

    time.sleep(.1)
    r = session.get("http://loclhost:%s/mailpile/%s/tags/as.json")

    print r.text

    tags_dict = r.json


    time.sleep(.1)
    print "\n================ "
    print "Setting up mailbox"
    setup_mailbox_data = {
        "mailbox.0001.primary_tag": "cloudfleet",
        "mailbox.0001.apply_tags[]": "c",
        "mailbox.0001.policy": "read",
        "_section": "sources.%s" % source_id
    }
    r = session.post("http://localhost:%s/mailpile/%s/api/0/settings/set/" % (port, username), data=setup_mailbox_data)
    print r.text


def handle(event):
    if event.get('action') == 'create' and event.get('username'):

        username = event.get('username')
        password = event.get('password')
        domain = event.get('domain')

        if os.path.isfile(settings.PORT_ASSIGNMENT_FILE_LOCATION):
            port_assignments = json.load(open(settings.PORT_ASSIGNMENT_FILE_LOCATION))
        else:
            port_assignments = {}


        directory = "/opt/cloudfleet/common/mails/%s/" % username
        for subdir in ["cur", "tmp", "new"]:
            subdir_path = "%s/%s" % (directory, subdir)
            if not os.path.exists(subdir_path):
                os.makedirs(subdir_path)


        print "Creating mailpile container for user " + event.get("username")

        c = docker.Client()
        c.pull(settings.MAILPILE_DOCKER_IMAGE)

        container_id = "mailpile-" + username

        if container_id in port_assignments:
            port = port_assignments.get(container_id)
        else:
            if len(port_assignments):
                port = sorted(port_assignments.values(), reverse=True)[0] + 1
            else:
                port = 20001

            port_assignments[container_id] = port
            if not os.path.exists(os.path.dirname(settings.PORT_ASSIGNMENT_FILE_LOCATION)):
                os.makedirs(os.path.dirname(settings.PORT_ASSIGNMENT_FILE_LOCATION))
            with open(settings.PORT_ASSIGNMENT_FILE_LOCATION, 'w') as port_assignments_file:
                json.dump(port_assignments, port_assignments_file) #FIXME make atomic

        container = c.create_container(
            settings.MAILPILE_DOCKER_IMAGE,
            name=container_id,
            volumes=[
                "/root/.local/share/Mailpile/",
                "/opt/cloudfleet/Mails/",
                "/etc/hosts"
            ],
            environment={
                "CLOUDFLEET_USERNAME": username,
            }
        )

        c.start(
            container,
            port_bindings={33411: port},
            binds={
                '/opt/cloudfleet/common/mails/%s/' % username:
                {
                    'bind': "/opt/cloudfleet/Mails/",
                    'ro': False
                },
                '/opt/cloudfleet/apps/mailpile/%s/data/' % username:
                {
                    'bind': "/root/.local/share/Mailpile/",
                    'ro': False
                },
                '/etc/hosts':
                {
                    'bind': "/etc/hosts",
                    'ro': True
                },
            }
        )
        print "Creating nginx configuration for mailpile container"
        template = settings.JINJA_ENV.get_template("user-app.conf.tpl")
        configuration = template.render(path="mailpile/" + username, port=port)

        if not os.path.exists(settings.NGINX_CONFIG_DIR):
            os.makedirs(settings.NGINX_CONFIG_DIR)

        with open(settings.NGINX_CONFIG_DIR + "/" + container_id + ".conf", "w") as fh:
            fh.write(configuration)

        print "================"
        print "Restarting nginx"
        nginx_restart_command = 'sudo service nginx restart'

        p = subprocess.Popen(nginx_restart_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        output = p.stdout.read()
        print output


        #return


        setup_mailpile(domain, password, port,username)


    else:
        print str(event)
