from socketio import Client
import json


# Class which acts as an abstraction of the robot on the server
class RobotClient():
    # Method to initialize the client
    def __init__(self, verbose=False):
        self.sio = Client()
        # here we keep track of the current target positions of the robot
        self.jointAngles = [0, 0, 0]
        self.verbose = verbose

        # here we listen to a specific response from the server, in this case jointUpdate
        @self.sio.on('jointUpdate')
        def on_message(data):
            # so in this case we just print that the joint was updated
            if self.verbose:
                print('Joint updated: ', data)
                print('>', end="")

        # when we get a jointStart, we update the jointAngles
        @self.sio.on('jointStart')
        def on_start(data):
            self.jointAngles = json.loads(data)
            if self.verbose:
                print('All joints updated: ', self.jointAngles)
                print('>', end="")

        # Here we connect to the server
        self.sio.connect('http://hannesarni.com:3100')
        # we poll the server for the current angle positions
        self.sio.emit('start', '')

    def move_joint1(self, degrees, velocity=200):
        self.jointAngles[0] = degrees
        self.sio.emit('jointUpdate', json.dumps({
            "jointIndex": 0,
            "degs": degrees,
            "vel": velocity
        }))

    def move_joint2(self, degrees, velocity=200):
        self.jointAngles[1] = degrees
        self.sio.emit('jointUpdate', json.dumps({
            "jointIndex": 1,
            "degs": degrees,
            "vel": velocity
        }))
