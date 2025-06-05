import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image, LaserScan
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class EnterTunnel(Node):
    def __init__(self):
        super().__init__('tunnel_sign_follower')

        self.bridge = CvBridge()
        self.cmd_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            10)
        self.br = CvBridge()
        self.frame = None
        self.laser_sub = self.create_subscription(LaserScan, '/scan', self.laser_callback, 10)
        self.laser_scan = None

        self.timer = self.create_timer(0.1, self.timer_callback)

        self.tunnel_detected = False
        self.wall_on_right = False

        self.forward_cmd = Twist()
        self.forward_cmd.linear.x = 0.2

        self.stop_cmd = Twist()  # All velocities = 0

        self.get_logger().info("Tunnel sign follower node started.")

    def listener_callback(self, data):
        self.frame = self.br.imgmsg_to_cv2(data, desired_encoding='bgr8')

    def laser_callback(self, msg):
        self.laser_scan = msg.ranges

    def timer_callback(self):
        if self.tunnel_detected:
            self.get_logger().info("Tunnel")
            right_indices = range(265, 275)  # adjust for your lidar's field of view
            right_distances = [self.laser_scan[i] for i in right_indices if not np.isnan(self.laser_scan[i])]
            
            if right_distances and min(right_distances) < 1.5:  # Wall closer than 0.5m
                self.get_logger().info("Wall detected on the right. Stopping.")
                self.wall_on_right = True
                self.cmd_pub.publish(self.stop_cmd)
            return
        if self.laser_scan is None or self.frame is None:
            self.get_logger().info("Rettt")
            return

        #self.frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')

        # Convert to HSV and detect a blue tunnel sign (adjust range as needed)
        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        # Red color mask (combined for red hue wrap-around)
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([160, 70, 50])
        upper_red2 = np.array([180, 255, 255])
        mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 1000:
                continue

            approx = cv2.approxPolyDP(cnt, 0.04 * cv2.arcLength(cnt, True), True)

            if len(approx) == 3:
                self.get_logger().info("Red triangle detected!")
                self.tunnel_detected = True
                self.cmd_pub.publish(self.forward_cmd)
                break


def main(args=None):
    rclpy.init(args=args)
    node = EnterTunnel()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
