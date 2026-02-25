#!/usr/bin/env python3
"""
Script de debug pour vérifier les commandes envoyées au drone
Usage: python3 debug_rl_commands.py
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
import time


class CommandDebugger(Node):
    def __init__(self):
        super().__init__('command_debugger')
        
        # Subscribe to topics
        self.input_sub = self.create_subscription(
            Twist, '/crazyflie/input_cmd_vel', self.input_callback, 10
        )
        self.output_sub = self.create_subscription(
            Twist, '/crazyflie/cmd_vel', self.output_callback, 10
        )
        self.odom_sub = self.create_subscription(
            Odometry, '/crazyflie/odom', self.odom_callback, 10
        )
        
        self.input_cmd = None
        self.output_cmd = None
        self.current_pos = None
        self.last_print = time.time()
        
        # Timer pour afficher toutes les 1s
        self.timer = self.create_timer(1.0, self.print_status)
        
        self.get_logger().info('🔍 Command Debugger Started')
    
    def input_callback(self, msg):
        """RL → control_services"""
        self.input_cmd = msg
    
    def output_callback(self, msg):
        """control_services → driver"""
        self.output_cmd = msg
    
    def odom_callback(self, msg):
        """Position actuelle"""
        self.current_pos = msg.pose.pose.position
    
    def print_status(self):
        """Affiche l'état toutes les secondes"""
        print("\n" + "="*70)
        print(f"ÉTAT À t={time.time():.1f}")
        print("="*70)
        
        # Position actuelle
        if self.current_pos:
            print(f"📍 POSITION : x={self.current_pos.x:.3f}  y={self.current_pos.y:.3f}  z={self.current_pos.z:.3f}")
        else:
            print("📍 POSITION : Pas de données")
        
        # Commandes INPUT (RL)
        if self.input_cmd:
            print(f"🤖 INPUT (RL Model) :")
            print(f"   linear  : x={self.input_cmd.linear.x:.3f}  y={self.input_cmd.linear.y:.3f}  z={self.input_cmd.linear.z:.3f}")
            print(f"   angular : z={self.input_cmd.angular.z:.3f}")
        else:
            print("🤖 INPUT (RL Model) : Pas de commandes")
        
        # Commandes OUTPUT (control_services)
        if self.output_cmd:
            print(f"🎮 OUTPUT (Control Services) :")
            print(f"   linear  : x={self.output_cmd.linear.x:.3f}  y={self.output_cmd.linear.y:.3f}  z={self.output_cmd.linear.z:.3f}")
            print(f"   angular : z={self.output_cmd.angular.z:.3f}")
        else:
            print("🎮 OUTPUT (Control Services) : Pas de commandes")
        
        # Vérifications
        print("\n🔍 VÉRIFICATIONS :")
        
        if self.input_cmd and self.output_cmd:
            # Vérifier si control_services modifie les commandes
            if (abs(self.input_cmd.linear.x - self.output_cmd.linear.x) > 0.01 or
                abs(self.input_cmd.linear.y - self.output_cmd.linear.y) > 0.01):
                print("   ⚠️  control_services MODIFIE les commandes XY (normal en mode IDLE)")
            else:
                print("   ✅ control_services TRANSMET les commandes XY (mode FLYING)")
            
            if abs(self.output_cmd.linear.z) > 0.01:
                print(f"   ⚠️  Commande Z non nulle : {self.output_cmd.linear.z:.3f} (devrait être 0)")
            else:
                print("   ✅ Commande Z = 0 (mode height-hold actif)")
        
        if self.current_pos and self.current_pos.z < 0.01:
            print("   ❌ DRONE AU SOL (z < 0.01)")
        elif self.current_pos and 0.4 < self.current_pos.z < 0.6:
            print(f"   ✅ DRONE À ALTITUDE CORRECTE (z={self.current_pos.z:.3f})")
        elif self.current_pos:
            print(f"   ⚠️  Altitude inattendue : z={self.current_pos.z:.3f}")


def main(args=None):
    rclpy.init(args=args)
    debugger = CommandDebugger()
    
    try:
        rclpy.spin(debugger)
    except KeyboardInterrupt:
        print("\n👋 Debug terminé")
    finally:
        debugger.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
