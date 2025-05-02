import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class FollowTheWall(Node):
    def __init__(self):
        super().__init__('follow_wall')

        self.pub_vel = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        self.laser_scan = None

        self.timer = self.create_timer(0.1, self.timer_callback)

    def scan_callback(self, msg):
        self.laser_scan = msg.ranges


    def timer_callback(self):
        if self.laser_scan is None:
            return

        msg = Twist()
        if self.laser_scan[0] > 1:
            
            msg.linear.x = 0.2        
            msg.angular.z = 0.0

        # Stop if wall is detected
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info("Wall Detected! Stopping")
            while self.laser_scan[90] > 1.5:
                msg.linear.x = 0.0
                msg.angular.z = 0.1 if (self.laser_scan[86] - self.laser_scan[94]) < 0.01 else (self.laser_scan[86] - self.laser_scan[94])
                self.get_logger().info("Turning")
                self.pub_vel.publish(msg)

        self.pub_vel.publish(msg)
        self.get_logger().info(
            f'Distance: {self.laser_scan[0]:.2f}, Publishing linear.x={msg.linear.x:.2f}, angular.z={msg.angular.z:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = FollowTheWall()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
