from flask import Flask, jsonify, request
import settings, traceback, getopt, sys

app = Flask(__name__)


@app.route('/bus/<channel>', methods=['POST'])
def post_message(channel):
    if channel in settings.channels:
        for plugin in settings.channels.get(channel):
            try:
                plugin(request.json)
            except:
                print traceback.format_exc()

    # TODO propagate to subscribers
    return jsonify({"message": "received", "status": "success"})

opts, args = getopt.getopt(sys.argv[1:], "h:", ["host="])

options = dict(opts)

hostname = "blimp-docker"

if "-h" in options:
    hostname = options["-h"]

if "--host" in options:
    hostname = options["--host"]

if __name__ == '__main__':
    app.run(host=hostname)
