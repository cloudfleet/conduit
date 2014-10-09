import docker, os.path, settings, json, subprocess


def handle(event):
    if event.get('action') == 'create' and event.get('username'):

        username = event.get('username')

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
                "/.share/local/Mailpile",
                "/opt/cloudfleet/data"
            ],
            environment={
                "CLOUDFLEET_USERNAME": username,
                "CLOUDFLEET_PASSWORD": "password",
            }
        )

        c.start(
            container,
            port_bindings={33411: port},
            binds={
                '/opt/cloudfleet/maildir/%s/' % username:
                {
                    'bind': "/opt/cloudfleet/data/",
                    'ro': False
                },
                '/opt/cloudfleet/apps/mailpile/%s/data/' % username:
                {
                    'bind': "/root/.share/local/Mailpile/",
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

        print "Restarting nginx \n"
        nginx_restart_command = 'sudo service nginx restart'

        p = subprocess.Popen(nginx_restart_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
        output = p.stdout.read()
        print output

    else:
        print str(event)
