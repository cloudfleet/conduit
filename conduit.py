from flask import Flask, jsonify, request
import settings, traceback

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


if __name__ == '__main__':
    app.run(host="0.0.0.0")
