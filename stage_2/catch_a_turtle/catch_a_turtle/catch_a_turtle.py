import rclpy
from rclpy.node import Node
import math
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class CatchTurtle(Node):
    def __init__(self):
        super().__init__('catch_a_turtle')

        self.pub = self.create_publisher(Twist, '/turtle2/cmd_vel', 10)
        self.sub_turtle1 = self.create_subscription(Pose, '/turtle1/pose', self.turtle1_callback, 10)
        self.sub_turtle2 = self.create_subscription(Pose, '/turtle2/pose', self.turtle2_callback, 10)

        self.turtle1_pose = None
        self.turtle2_pose = None

        self.timer = self.create_timer(0.1, self.timer_callback)

    def turtle1_callback(self, msg):
        self.turtle1_pose = (msg.x, msg.y)

    def turtle2_callback(self, msg):
        self.turtle2_pose = (msg.x, msg.y, msg.theta)

    def timer_callback(self):
        if self.turtle1_pose is None or self.turtle2_pose is None:
            return

        x1, y1 = self.turtle1_pose
        x2, y2, theta2 = self.turtle2_pose

        # Compute distance
        dx = x1 - x2
        dy = y1 - y2
        distance = math.sqrt(dx**2 + dy**2)

        # Compute angle to turtle1
        target_angle = math.atan2(dy, dx)

        # Normalize angular difference
        angular_diff = target_angle - theta2
        angular_diff = (angular_diff + math.pi) % (2 * math.pi) - math.pi

        # Proportional control for linear and angular velocity
        msg = Twist()
        msg.linear.x = min(2.0, 1.5 * distance)        # Faster when far away
        msg.angular.z = 4.0 * angular_diff             # Turn faster if angle is big

        # Stop if we're very close
        if distance < 0.5:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.get_logger().info("Turtle2 caught Turtle1")

        self.pub.publish(msg)
        self.get_logger().info(
            f'Distance: {distance:.2f}, Publishing linear.x={msg.linear.x:.2f}, angular.z={msg.angular.z:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = CatchTurtle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
