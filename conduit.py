from flask import Flask, jsonify, request
import settings, traceback, getopt, sys, os


app = Flask(__name__)


@app.route('/bus/<channel>', methods=['POST'])
def post_message(channel):
    if channel in settings.channels:
        for plugin in settings.channels.get(channel):
            try:
                plugin(request.get_json(force=True))
            except:
                print traceback.format_exc()

    # TODO propagate to subscribers
    return jsonify({"message": "received", "status": "success"})

if __name__ == '__main__':
    print os.environ
    app.run(host='0.0.0.0')
