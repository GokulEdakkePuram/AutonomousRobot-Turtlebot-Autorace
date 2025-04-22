import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose
import math

class CountCircles(Node):
    def __init__(self):
        super().__init__('count_circles')
        self.sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        
        self.pose = None
        self.init_pose = None
        self.left_start = False
        self.circle_counter = 0
        self.threshold = 0.5  # dist to check returned to start pose

    def pose_callback(self, msg: Pose):
        self.pose = (msg.x, msg.y)

    def check_circle_complete(self):
        if self.pose is None:
            return

        if self.init_pose is None:
            self.init_pose = self.pose
            self.get_logger().info(f"Initial position set to: {self.init_pose}")
            return

        dist = math.dist(self.pose, self.init_pose)

        if dist > self.threshold:
            self.left_start = True

        if dist <= self.threshold and self.left_start:
            self.circle_counter += 1
            self.left_start = False
            self.get_logger().info(f"Circle Count: {self.circle_counter}")


def main(args=None):
    rclpy.init(args=args)
    node = CountCircles()

    while rclpy.ok():
        rclpy.spin_once(node, timeout_sec=0.1)
        node.check_circle_complete()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
