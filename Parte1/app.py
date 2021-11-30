import flask
from flask.json import jsonify
import uuid
import os
from main import Store

simulations = {}

app = flask.Flask(__name__)

@app.route("/simulation", methods=["POST"])
def create():
    global simulations
    id = str(uuid.uuid4())
    simulations[id] = Store()
    return "ok", 201, {'Location': f"/simulation/{id}", "Items": len(simulations[id].schedule.agents)}

@app.route("/simulation/<id>", methods=["GET"])
def queryState(id):
    global model
    model = simulations[id]
    model.step()
    agents = []
    for agent in model.schedule.agents:
      if agent.pos is not None:
      	agents.append({"typeAgent": type(agent).__name__, "condition": agent.condition,  "x": agent.pos[0], "y": agent.pos[1]})
    return jsonify({"Items": agents})
app.run()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5001)))
