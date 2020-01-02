import math
from socketClient import RobotClient
import time

ROD1LENGTH = 130
ROD2LENGTH = 100


# Function which calculates the length of the robot on the x-axis in centimeters
def get_length_cm(joint1_rad, joint2_rad):
    return ROD1LENGTH * math.cos(joint1_rad) + ROD2LENGTH * math.cos(joint2_rad)


# Function for finding the rotation angle of the first joint in degrees
def get_joint1_deg(x, height):
    # Initializing range for binary search
    left_index = 0
    right_index = 90
    # Repeat while the range is bigger than 0.001
    while abs(right_index - left_index) > 0.001:
        # Find the middle of the range which acts temporarily as the rotation angle of the first joint
        mid = (right_index + left_index) / 2
        # Calculates the rotation angle of the second joint
        joint2tmp = get_joint2_deg(math.radians(mid), height)
        # Calculates the total length of the robot in centimeters
        val = get_length_cm(math.radians(90 - mid), math.radians(joint2tmp + mid - 90))
        # If the length is smaller than the desired distance, we make the first joint rotation angle smaller
        # Otherwise, we make it larger
        if val < float(x):
            left_index = mid
        else:
            right_index = mid
    # Returns the left end of the range, although the range has gotten so small it does not matter which you return
    return left_index


# Function for finding the rotation angle of the second joint in degrees
def get_joint2_deg(first_joint_rad, surface_height):
    checking_value = (-ROD1LENGTH * math.sin(math.pi / 2 - first_joint_rad) + surface_height) / ROD2LENGTH
    # Checks to see if the desired movement is possible. I will possibly implement error flag for this stuff later
    # The value of checking_value will become larger than 1 or smaller than -1 if the movement is not possible
    if checking_value > 1:
        exit(-1)
    if checking_value < -1:
        exit(-1)
    # Finish the calculation
    return 180 - math.degrees(first_joint_rad + math.pi / 2 + math.asin(checking_value))


# Main Function
if __name__ == "__main__":
    # Initializes the socket client
    robot = RobotClient()

    # Start endless loop
    while True:
        # Takes in the desired position on the 2d plane
        desiredX, desiredY = map(float, input('>').split(' '))

        # Calculates the rotational angles of the joints
        joint1 = get_joint1_deg(desiredX, desiredY)
        joint2 = get_joint2_deg(math.radians(joint1), desiredY)

        current_joint1 = robot.jointAngles[0]
        current_joint2 = robot.jointAngles[1]

        currentX = get_length_cm(math.radians(90-current_joint1), math.radians(current_joint2 + current_joint1 - 90))

        cur = currentX

        while True:
            j1 = get_joint1_deg(cur,desiredY)
            j2 = get_joint2_deg(math.radians(j1),desiredY)
            robot.move_joint1(j1)
            robot.move_joint2(j2)
            if desiredX > currentX:
                cur += 0.5
                if cur > desiredX:
                    break
            else:
                cur -= 0.5
                if cur < desiredX:
                    break
            time.sleep(0.05)

        robot.move_joint1(joint1)
        robot.move_joint2(joint2)

        """iteration = (joint1-current_joint1)/20
        print(iteration)
        current = current_joint1
        for x in range(21):
            print(current)
            robot.move_joint1(current)
            robot.move_joint2(get_joint2_deg(math.radians(current), desiredY))
            current += iteration
            time.sleep(0.5)
        # checking the change of angles
        joint1Diff = abs(current_joint1 - joint1)
        joint2Diff = abs(current_joint2 - joint2)

        # how long the movement will take in seconds
        moveSpeed = max(joint1Diff, joint2Diff) / 20
        joint1Vel = joint1Diff / moveSpeed
        joint2Vel = joint2Diff / moveSpeed

        # Calls the robot to move its butt
        robot.move_joint1(joint1, joint1Vel)
        robot.move_joint2(joint2, joint2Vel)"""
