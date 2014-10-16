import docker, os.path, settings, json, subprocess, requests


def handle(event):
    if event.get('action') == 'create' and event.get('username'):

        username = event.get('username')
        password = event.get('password')

        if os.path.isfile(settings.PORT_ASSIGNMENT_FILE_LOCATION):
            port_assignments = json.load(open(settings.PORT_ASSIGNMENT_FILE_LOCATION))
        else:
            port_assignments = {}

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
                "/root/.local/share/Mailpile",
                "/opt/cloudfleet/data"
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
                    'bind': "/opt/cloudfleet/data/",
                    'ro': False
                },
                '/opt/cloudfleet/apps/mailpile/%s/data/' % username:
                {
                    'bind': "/root/.local/share/Mailpile/",
                    'ro': False
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


        session = requests.session()

        print "\n================"
        print "Setting up passphrase"

        setup_crypto_data = {
            'passphrase': password,
            'passphrase_confirm': password,
            'choose_key': '!CREATE',
        }
        r = session.post("http://localhost:%s/mailpile/%s/setup/crypto/as/json" % (port, username), data=setup_crypto_data)

        print r.text

        print "\n================ "
        print "Setting up smtp server"

        route_id = "5603a8l6kqog8pvi" # FIXME create random? check how mailpile does it

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



        print "\n================ "
        print "Setting up profile"

        setup_profile_data = {
            "name": username,
            "email": "%s@%s" % (username, os.environ.get('CLOUDFLEET_DOMAIN', 'example.com')),
            "pass": "25",
            "route_id": route_id,
            "note": "CloudFleet default route"
        }
        r = session.post("http://localhost:%s/mailpile/%s/api/0/setup/profiles/" % (port, username), data=setup_profile_data)

        print r.text



    else:
        print str(event)
