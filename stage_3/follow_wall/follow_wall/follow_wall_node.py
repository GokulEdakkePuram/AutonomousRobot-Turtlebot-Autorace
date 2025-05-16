import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class FollowTheWall(Node):
    def __init__(self):
        super().__init__('follow_wall')

        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.scan = self.create_subscription(LaserScan, '/scan', self.scan_callback, 10)

        self.LaserData = None

        self.parallel_threshold = 0.005  # Threshold for being parallel to the wall
        self.turning_right = False
        self.turning_left = False
        self.FrontDist = 2.0


        self.timer = self.create_timer(0.1, self.timer_callback)

    def scan_callback(self, msg):
        self.LaserData = msg.ranges
        self.LaserData = [0.0 if x == float('inf') else -0.0 if x == -float('inf') else x for x in self.LaserData]
        self.max_range = msg.range_max


    def timer_callback(self):
        if self.LaserData is None:
            return

        msg = Twist()
        turn = False
        if self.turning_right is True:
            # Check if robot is parallel to the wall
            #if abs(self.LaserData[85] - self.LaserData[95]) < self.parallel_threshold:
            #while turn and round((abs(self.LaserData[90] - self.FrontDist)), 3) > 0.01:
            while turn and (abs(self.LaserData[86+180] - self.LaserData[94+180])) > 0.005 and round((abs(self.LaserData[90+180] - self.FrontDist)), 3) > 0.01:
                msg.angular.z = 0.1
                msg.linear.x = 0.0
                self.cmd_vel_pub.publish(msg)
                #self.get_logger().info('Initial left turn')
                #self.get_logger().info(round(abs(self.LaserData[270] - self.FrontDist), 3))
                #rospy.sleep(0.5)
            turn = False
            if abs((self.LaserData[86+180]) - (self.LaserData[94+180])) > self.parallel_threshold:
                if self.LaserData[0] < 0.5 and self.LaserData[0] > 0.0:
                    msg.angular.z = 0.4
                    msg.linear.x = 0.0
                    self.turning_right = False
            #if (self.LaserData[90]-self.FrontDist) > 0.01: 
                # Stop turning
                msg.angular.z = 0.0
                msg.linear.x = 0.0
                
                error = self.LaserData[86+180]-self.LaserData[94+180]
                #self.get_logger().info("Error:", error)
                #if max(self.LaserData[slice(89,91)]) == float('inf'):
                #self.get_logger().info(self.LaserData[slice(89,91)])
                while min(self.LaserData[slice((88+180),(92+180))]) == 0.0:
                #if error > 0.1:
                
                    error = 0.01
                    #self.get_logger().info('In while INF')
                    if abs(error) > 0.1:
                        fact = 1.0
                    else:
                        fact = 10.0
                    msg.linear.x = 0.0  
                    msg.angular.z = error * fact
                    #self.get_logger().info(f"ang z: {error*fact}")
                    self.cmd_vel_pub.publish(msg)
                '''if error < -0.1:
                    error = -0.01
                    self.get_logger().info('-INF')'''
                if abs(error) > 0.1:
                    fact = 1.5
                else:
                    fact = 10.0
                #self.get_logger().info(error)
                msg.linear.x = 0.0  
                msg.angular.z = error * fact 
            else:
                msg.linear.x = 1.5
                msg.angular.z =0.0
        
        elif min(min(self.LaserData[slice(0,5)]),min(self.LaserData[slice(350,360)])) < self.FrontDist:
            
            # Stop moving forward
            msg.linear.x = 0.0
            # Start turning left until parallel to the wall
            msg.angular.z = 1.0
            self.turning_right = True
            turn = True
            #self.get_logger().info(len(self.))
        else:
            # Move forward
            #self.get_logger().info(f'normal front {self.LaserData[0]}')
            msg.linear.x = 1.5
            # Stop turning
            msg.angular.z = 0.0


        self.cmd_vel_pub.publish(msg)
        self.get_logger().info(
            f'Distance: {self.LaserData[0]:.2f}, Publishing linear.x={msg.linear.x:.2f}, angular.z={msg.angular.z:.2f}'
        )

def main(args=None):
    rclpy.init(args=args)
    node = FollowTheWall()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
