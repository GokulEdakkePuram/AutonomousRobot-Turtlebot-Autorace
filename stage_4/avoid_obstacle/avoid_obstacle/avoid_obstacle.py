import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Image
from geometry_msgs.msg import Twist
from rclpy.executors import ExternalShutdownException, MultiThreadedExecutor
from rclpy.callback_groups import MutuallyExclusiveCallbackGroup, ReentrantCallbackGroup
from cv_bridge import CvBridge
import cv2
import numpy as np

class LineWallNavigator(Node):
    def __init__(self):
        super().__init__('line_wall_navigator')

        self.image = None
        self.laser_data = None

        laser_cb_group = MutuallyExclusiveCallbackGroup()
        timer_cb_group = MutuallyExclusiveCallbackGroup()
        timer2_cb_group = MutuallyExclusiveCallbackGroup()

        # Subscriptions
        self.create_subscription(LaserScan, '/scan', self.lidar_callback, 10, callback_group=laser_cb_group)
        self.create_subscription(Image, '/camera/image_raw', self.camera_callback, 10)

        # Publisher
        self.velocity_publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # Timer for control loop
        self.create_timer(0.1, self.control_loop, callback_group=timer_cb_group)
        self.create_timer(0.1, self.data_proc, callback_group=timer2_cb_group)

        # Bridge for image conversion
        self.cv_bridge = CvBridge()

        # Sensor states
        self.dist_ahead = float('inf')
        self.dist_right = float('inf')
        self.front_right_open = False

        # Behavior states
        self.in_wall_follow_mode = False
        self.detected_line = False
        self.has_turned = False
        self.turn_counter = 0
        self.in_turn_sequence = False

    def lidar_callback(self, scan_msg):
        self.laser_data = scan_msg

    def camera_callback(self, img_msg):
        try:
            self.image = self.cv_bridge.imgmsg_to_cv2(img_msg, desired_encoding='bgr8')
        except Exception as err:
            self.get_logger().error(f"Image conversion failed: {err}")
            return

        

        # # Show debug windows
        # cv2.rectangle(image, (int(0.35 * w), int(0.7 * h)), (int(0.65 * w), h), (0, 255, 0), 2)
        # cv2.imshow("View", image)
        # cv2.imshow("ROI", roi)
        # cv2.waitKey(1)

    def get_min_valid(self, data):
        valid = [d for d in data if 0.05 < d < float('inf')]
        return min(valid) if valid else float('inf')
    
    def data_proc(self):
        if self.image is None or self.laser_data is None:
            return
        h, w = self.image.shape[:2]
        roi = self.image[int(0.7 * h):, int(0.35 * w):int(0.65 * w)]
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)

        white_area = cv2.countNonZero(thresh) / thresh.size
        self.detected_line = white_area > 0.2 and not self.has_turned

        self.dist_ahead = self.get_min_valid(self.laser_data.ranges[320:360] + self.laser_data.ranges[0:5])
        self.dist_right = self.get_min_valid([self.laser_data.ranges[i] for i in range(250, 290)])
        front_right = self.get_min_valid([self.laser_data.ranges[i] for i in range(30, 60)])
        self.front_right_open = front_right > 0.6

    def control_loop(self):
        if self.image is None or self.laser_data is None:
            return
        twist = Twist()
        target_distance = 0.18
        stop_distance = 0.25

        # Trigger line-based turn once
        if self.detected_line and not self.has_turned and not self.in_turn_sequence:
            self.in_turn_sequence = True
            self.turn_counter = 0
            self.get_logger().info("White line spotted, beginning left turn")

        # If in line-turning sequence
        if self.in_turn_sequence:
            twist.linear.x = 0.0
            twist.angular.z = 0.5
            self.turn_counter += 1

            if self.turn_counter >= 20:
                self.in_turn_sequence = False
                self.has_turned = True
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.get_logger().info("Turn finished")

            self.velocity_publisher.publish(twist)
            return

        # After turning, stop all motion
        if self.has_turned:
            self.velocity_publisher.publish(twist)
            return

        # Obstacle-following logic
        if self.dist_ahead < stop_distance or self.in_wall_follow_mode:
            self.in_wall_follow_mode = True

            if self.dist_ahead < stop_distance:
                twist.linear.x = 0.0
                twist.angular.z = 0.35
                self.get_logger().info("Obstacle ahead — turning left")
            elif self.front_right_open:
                twist.linear.x = 0.1
                twist.angular.z = -0.35
                self.get_logger().info("Lost wall front-right — turning right")
            else:
                error = self.dist_right - target_distance
                twist.linear.x = 0.1
                twist.angular.z = -3.4 * error
                self.get_logger().info(f"Wall-following with error: {error:.2f}")

        else:
            twist.linear.x = 0.1
            twist.angular.z = 0.0
            self.in_wall_follow_mode = False
            self.get_logger().info("Clear path — moving forward")

        self.velocity_publisher.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = LineWallNavigator()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    executor.spin()
    #node.destroy_node()
    cv2.destroyAllWindows()
    rclpy.shutdown()

if __name__ == '__main__':
    main()