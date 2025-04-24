import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from std_msgs.msg import Int32

from turtlemover.count_circles import CountCircles

class MoveTurtle(Node):
    def __init__(self):
        super().__init__('move_turtle')
        self.pub_vel = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pub_circles = self.create_subscription(Int32, '/move_turtle_circles', self.circle_callback, 10)
        #self.timer = self.create_timer(0.5, self.timer_callback)
        self.count = 0
        self.no_circles = 0
        self.moving = False

    def timer_callback(self):
        msg = Twist()
        msg.linear.x = 1.0
        msg.angular.z = 0.4
        self.pub_vel.publish(msg)

    def circle_callback(self, msg):
        self.no_circles = msg.data
        self.get_logger().info(f"Got no. circles: {self.no_circles}")
        self.run()

    def run(self):
        if not self.moving:
            self.moving = True
            self.timer = self.create_timer(0.5, self.timer_callback)
            #self.get_logger().info("Moving!")

    def stop(self):
        msg = Twist()
        msg.linear.x = 0.0
        msg.angular.z = 0.0
        self.pub_vel.publish(msg)



def main(args=None):
    rclpy.init(args=args)

    move_turtle = MoveTurtle()
    count_circles = CountCircles()

    while rclpy.ok():
        rclpy.spin_once(move_turtle)
        rclpy.spin_once(count_circles)

        if move_turtle.moving:
            #while move_turtle.count <= move_turtle.no_circles:
            #move_turtle.run()
            count_circles.check_circle_complete()
            move_turtle.count = count_circles.circle_counter
            
            if move_turtle.count >= move_turtle.no_circles:
                move_turtle.stop()
                break


    #rclpy.spin(move_turtle)

    # Destroy the node explicitly
    # (optional - otherwise it will be done automatically
    # when the garbage collector destroys the node object)
    move_turtle.destroy_node()
    rclpy.shutdown()



if __name__ == '__main__':
    main()
