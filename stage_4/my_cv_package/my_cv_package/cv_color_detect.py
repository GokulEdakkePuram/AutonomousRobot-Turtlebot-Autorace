import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from geometry_msgs.msg import Twist
from cv_bridge import CvBridge
import cv2
import numpy as np

class LaneFollower(Node):
    def __init__(self):
        super().__init__('lane_follower')
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.listener_callback,
            10)
        self.br = CvBridge()
        self.frame = None
        self.timer = self.create_timer(0.1, self.timer_callback)

    def listener_callback(self, data):
        self.frame = self.br.imgmsg_to_cv2(data, desired_encoding='bgr8')

    def timer_callback(self):
        if self.frame is None:
            return

        hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
        height, width, _ = hsv.shape

        # HSV thresholds for white and yellow
        yellow_lower = np.array([20, 100, 100])
        yellow_upper = np.array([30, 255, 255])
        white_lower = np.array([0, 0, 200])
        white_upper = np.array([180, 50, 255])

        yellow_mask = cv2.inRange(hsv, yellow_lower, yellow_upper)
        white_mask = cv2.inRange(hsv, white_lower, white_upper)
        lane_mask = cv2.bitwise_or(yellow_mask, white_mask)

        # Define ROI: bottom 40px, horizontally center 60%
        roi_vertical_start = height - 60
        roi_vertical_end = height - 20
        roi_horizontal_start = int(width * 0.2)
        roi_horizontal_end = int(width * 0.8)

        roi = lane_mask[roi_vertical_start:roi_vertical_end, roi_horizontal_start:roi_horizontal_end]

        # Moments for centroid
        moments = cv2.moments(roi)

        if moments["m00"] == 0:
            self.get_logger().warn("No lane detected in ROI!")
            return

        cx = int(moments["m10"] / moments["m00"]) + roi_horizontal_start
        error = (width / 2) - cx

        msg = Twist()
        msg.linear.x = 0.05 
        msg.angular.z = -float(error) / 500.0

        self.cmd_vel_pub.publish(msg)

        self.get_logger().info(
            f'Error: {error:.2f}, linear.x={msg.linear.x:.2f}, angular.z={msg.angular.z:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = LaneFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
