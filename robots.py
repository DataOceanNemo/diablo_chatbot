import threading
import time

import rclpy
from rclpy.node import Node
from motion_msgs.msg import MotionCtrl


class RosNode(Node):
    def __init__(self):
        super().__init__('flask_ros_node')
        self.publisher_ = self.create_publisher(
            MotionCtrl, "diablo/MotionCmd", 2)

    def publish_message(self, msg):
        self.publisher_.publish(msg)


rclpy.init()
ros_node = RosNode()

CMD_GO_FORWARD = 0x08
CMD_GO_LEFT = 0x04
CMD_ROLL_RIGHT = 0x09

CMD_HEIGH_MODE = 0x01
CMD_BODY_UP = 0x11

CMD_STAND_UP = 0x02
CMD_STAND_DOWN = 0x12

CMD_PITCH = 0x03
CMD_PITCH_MODE = 0x13

CMD_SPEED_MODE = 0x05


# Define the interval task
def interval_task():
    while not stop_event.is_set():
        # Perform the task action here
        msg = MotionCtrl()
        msg.cmd_id = 0
        msg.value = 0.0
        ros_node.publish_message(msg)

        # Wait for the specified interval
        time.sleep(interval)


# Define the interval duration in seconds
interval = 0.4

# Create a stop event to control the task execution
stop_event = threading.Event()


def activateMotionControl():
    # Reset the stop event
    stop_event.clear()

    # Create a new thread for the interval task
    task_thread = threading.Thread(target=interval_task)

    # Start the interval task thread
    task_thread.start()


def releaseMotionControl():
    stop_event.set()


def run_task_with_duration(cmd, value, duration):
    # Record the start time
    start_time = time.time()

    if duration > 2:
        # safety boundary
        duration = 2

    # Run the task until the duration is reached
    while time.time() - start_time < duration:
        msg = MotionCtrl()
        msg.cmd_id = cmd
        msg.value = value
        ros_node.publish_message(msg)


def move_forward(meter):
    run_task_with_duration(CMD_GO_FORWARD, 1.0, meter)


def move_backward(meter):
    run_task_with_duration(CMD_GO_FORWARD, -(1.0), meter)


def turn(degree):
    run_task_with_duration(CMD_GO_LEFT, -(1.0) if degree >
                           0 else 1.0, abs(degree // 100))


def stop():
    msg = MotionCtrl()
    msg.cmd_id = CMD_GO_FORWARD
    msg.value = 0.0
    ros_node.publish_message(msg)
    print('xxxxxx')
    msg2 = MotionCtrl()
    msg2.cmd_id = CMD_GO_LEFT
    msg2.value = 0.0
    ros_node.publish_message(msg2)
