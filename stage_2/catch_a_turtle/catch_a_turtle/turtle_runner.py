import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist

class TurtleMover(Node):
    def __init__(self):
        super().__init__('turtle_runner')
        self.turtle_name = 'turtle1'
        
        self.pub = self.create_publisher(Twist, f'/{self.turtle_name}/cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 1.0
        msg.angular.z = 0.4
        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    turtle_mover = TurtleMover()

    rclpy.spin(turtle_mover)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    turtle_mover.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()
