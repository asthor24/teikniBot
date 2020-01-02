from socketio import Client
import json


# Class which acts as an abstraction of the robot on the server
class RobotClient:
    # Method to initialize the client
    def __init__(self):
        self.sio = Client()

        # here we listen to a specific response from the server, in this case jointUpdate
        @self.sio.on('jointUpdate')
        def on_message(data):
            # so in this case we just print that the joint was updated
            print('Joint updated', data)
            print('>', end="")

        # Here we connect to the server
        self.sio.connect('http://hannesarni.com:3100')

    def move_joint1(self, degrees):
        self.sio.emit('jointUpdate', json.dumps({
            "jointIndex": 0,
            "degs": degrees,
            "vel": 200
        }))

    def move_joint2(self, degrees):
        self.sio.emit('jointUpdate', json.dumps({
            "jointIndex": 1,
            "degs": degrees,
            "vel": 200
        }))
