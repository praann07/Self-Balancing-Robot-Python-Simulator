"""
🏪 Professional Restaurant Supervisor Controller
Manages: Customer spawning, orders, robot coordination, real-time statistics

This supervisor controls the entire restaurant simulation:
- Spawns customers dynamically
- Manages order queue
- Assigns orders to available robots
- Tracks statistics and displays them
"""

from controller import Supervisor
import random
import time

class RestaurantSupervisor:
    def __init__(self):
        self.supervisor = Supervisor()
        self.timestep = int(self.supervisor.getBasicTimeStep())
        
        # Table information (11 tables)
        self.tables = [
            {'id': 1, 'pos': (-7, -7), 'seats': 2, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 2, 'pos': (-7, -4), 'seats': 2, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 3, 'pos': (-4, -7), 'seats': 4, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 4, 'pos': (-4, -4), 'seats': 4, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 5, 'pos': (-7, 4), 'seats': 2, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 6, 'pos': (-7, 7), 'seats': 2, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 7, 'pos': (-4, 4), 'seats': 4, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 8, 'pos': (-4, 7), 'seats': 4, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 9, 'pos': (-1, 0), 'seats': 2, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 10, 'pos': (-1, -7), 'seats': 6, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
            {'id': 11, 'pos': (-1, 7), 'seats': 6, 'occupied': False, 'customer': None, 'order_time': 0, 'has_food': False},
        ]
        
        # Customer colors (for variety)
        self.customer_colors = [
            (0.2, 0.4, 0.8),  # Blue
            (0.8, 0.2, 0.4),  # Red/Pink
            (0.4, 0.8, 0.2),  # Green
            (0.8, 0.6, 0.2),  # Orange/Yellow
            (0.6, 0.2, 0.8),  # Purple
            (0.2, 0.8, 0.8),  # Cyan
            (0.8, 0.4, 0.6),  # Pink
        ]
        
        # Statistics
        self.total_customers = 0
        self.total_orders = 0
        self.total_deliveries = 0
        self.waiting_orders = []
        self.active_customers = []
        self.customer_spawn_interval = 3000  # 3 seconds
        self.last_spawn_time = 0
        
        # Robot tracking
        self.robots = {
            'robot1': {'status': 'IDLE', 'assigned_order': None},
            'robot2': {'status': 'IDLE', 'assigned_order': None},
            'robot3': {'status': 'IDLE', 'assigned_order': None},
        }
        
        # Pickup counter position
        self.pickup_pos = (8, -7.5)
        
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║   🏪 PROFESSIONAL RESTAURANT SIMULATION - SUPERVISOR ACTIVE  ║")
        print("╠══════════════════════════════════════════════════════════════╣")
        print("║  📊 Dynamic Customer Spawning: ENABLED                        ║")
        print("║  🤖 Multi-Robot Coordination: 3 Robots                       ║")
        print("║  🍽️  Real-time Order Management: ACTIVE                      ║")
        print("║  ⏱️  Timing System: ON                                        ║")
        print("╚══════════════════════════════════════════════════════════════╝\n")
        
    def get_empty_tables(self):
        """Return list of unoccupied tables"""
        return [t for t in self.tables if not t['occupied']]
    
    def spawn_customer(self):
        """Spawn a new customer at an empty table"""
        empty_tables = self.get_empty_tables()
        
        if not empty_tables:
            return  # No empty tables
        
        # Pick random empty table
        table = random.choice(empty_tables)
        
        # Create customer node
        customer_id = f"customer_{self.total_customers + 1}"
        color = random.choice(self.customer_colors)
        
        # Customer spawn at entrance first
        entrance_pos = [-11.5, random.uniform(-2, 2), 0.85]
        
        # Calculate safe colors (clamp to [0, 1] range to avoid Webots errors)
        head_color = (min(color[0] * 1.2, 1.0), min(color[1] * 1.2, 1.0), min(color[2] * 1.2, 1.0))
        neck_color = (min(color[0] * 1.1, 1.0), min(color[1] * 1.1, 1.0), min(color[2] * 1.1, 1.0))
        pants_color = (color[0] * 0.4, color[1] * 0.4, color[2] * 0.4)
        
        # VRML/WBT string for realistic humanoid customer
        customer_def = f"""
        DEF {customer_id} Solid {{
          translation {entrance_pos[0]} {entrance_pos[1]} {entrance_pos[2]}
          children [
            # HEAD
            Transform {{
              translation 0 0 0.75
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {head_color[0]} {head_color[1]} {head_color[2]}
                    roughness 0.6
                    metalness 0.1
                  }}
                  geometry Sphere {{
                    radius 0.12
                    subdivision 2
                  }}
                }}
              ]
            }}
            # NECK
            Transform {{
              translation 0 0 0.6
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {neck_color[0]} {neck_color[1]} {neck_color[2]}
                    roughness 0.7
                  }}
                  geometry Cylinder {{
                    height 0.08
                    radius 0.05
                    subdivision 8
                  }}
                }}
              ]
            }}
            # TORSO (shirt color)
            Transform {{
              translation 0 0 0.4
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {color[0]} {color[1]} {color[2]}
                    roughness 0.8
                    metalness 0.05
                  }}
                  geometry Box {{
                    size 0.3 0.2 0.4
                  }}
                }}
              ]
            }}
            # LEFT ARM
            Transform {{
              translation 0 0.12 0.45
              rotation 1 0 0 0.3
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {color[0]} {color[1]} {color[2]}
                    roughness 0.8
                  }}
                  geometry Cylinder {{
                    height 0.35
                    radius 0.04
                    subdivision 8
                  }}
                }}
              ]
            }}
            # RIGHT ARM
            Transform {{
              translation 0 -0.12 0.45
              rotation 1 0 0 -0.3
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {color[0]} {color[1]} {color[2]}
                    roughness 0.8
                  }}
                  geometry Cylinder {{
                    height 0.35
                    radius 0.04
                    subdivision 8
                  }}
                }}
              ]
            }}
            # WAIST
            Transform {{
              translation 0 0 0.15
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {color[0] * 0.5} {color[1] * 0.5} {color[2] * 0.5}
                    roughness 0.9
                  }}
                  geometry Box {{
                    size 0.25 0.18 0.12
                  }}
                }}
              ]
            }}
            # LEFT LEG
            Transform {{
              translation 0 0.06 0.05
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {pants_color[0]} {pants_color[1]} {pants_color[2]}
                    roughness 0.9
                  }}
                  geometry Cylinder {{
                    height 0.5
                    radius 0.055
                    subdivision 8
                  }}
                }}
              ]
            }}
            # RIGHT LEG
            Transform {{
              translation 0 -0.06 0.05
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {pants_color[0]} {pants_color[1]} {pants_color[2]}
                    roughness 0.9
                  }}
                  geometry Cylinder {{
                    height 0.5
                    radius 0.055
                    subdivision 8
                  }}
                }}
              ]
            }}
            # LEFT FOOT
            Transform {{
              translation 0.08 0.06 -0.19
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor 0.2 0.2 0.2
                    roughness 0.95
                  }}
                  geometry Box {{
                    size 0.18 0.08 0.06
                  }}
                }}
              ]
            }}
            # RIGHT FOOT
            Transform {{
              translation 0.08 -0.06 -0.19
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor 0.2 0.2 0.2
                    roughness 0.95
                  }}
                  geometry Box {{
                    size 0.18 0.08 0.06
                  }}
                }}
              ]
            }}
          ]
          name "{customer_id}"
          boundingObject Box {{
            size 0.3 0.2 0.9
          }}
          physics Physics {{
            density -1
            mass 70
          }}
        }}
        """
        
        # Import customer
        root = self.supervisor.getRoot()
        children_field = root.getField('children')
        children_field.importMFNodeFromString(-1, customer_def)
        
        # Get customer node
        customer_node = self.supervisor.getFromDef(customer_id)
        
        # Mark table as occupied
        table['occupied'] = True
        table['customer'] = customer_id
        table['order_time'] = self.supervisor.getTime()
        table['has_food'] = False
        
        self.total_customers += 1
        self.active_customers.append({
            'id': customer_id,
            'node': customer_node,
            'table_id': table['id'],
            'target_pos': table['pos'],
            'status': 'WALKING_TO_TABLE',
            'order_placed': False
        })
        
        print(f"👤 Customer #{self.total_customers} arrived! Walking to Table {table['id']}...")
    
    def update_customers(self):
        """Move customers to their tables"""
        dt = self.timestep / 1000.0
        
        for customer in self.active_customers:
            if customer['status'] == 'WALKING_TO_TABLE':
                node = customer['node']
                if node:
                    pos = node.getPosition()
                    target = customer['target_pos']
                    
                    # Simple movement towards table
                    dx = target[0] - pos[0]
                    dy = target[1] - pos[1]
                    dist = (dx**2 + dy**2) ** 0.5
                    
                    if dist > 0.3:
                        # Move towards table
                        speed = 1.0
                        new_x = pos[0] + (dx / dist) * speed * dt
                        new_y = pos[1] + (dy / dist) * speed * dt
                        node.getField('translation').setSFVec3f([new_x, new_y, 0.85])
                    else:
                        # Arrived at table
                        node.getField('translation').setSFVec3f([target[0] + 0.3, target[1], 0.85])
                        customer['status'] = 'SEATED'
                        print(f"   ✅ Customer at Table {customer['table_id']} - SEATED")
            
            elif customer['status'] == 'SEATED' and not customer['order_placed']:
                # Place order after a moment
                table = self.tables[customer['table_id'] - 1]
                if self.supervisor.getTime() - table['order_time'] > 2:
                    customer['order_placed'] = True
                    self.create_order(customer['table_id'])
    
    def create_order(self, table_id):
        """Create a new food order for a table"""
        order = {
            'id': self.total_orders + 1,
            'table_id': table_id,
            'status': 'WAITING',
            'assigned_robot': None,
            'created_time': self.supervisor.getTime()
        }
        
        self.waiting_orders.append(order)
        self.total_orders += 1
        
        table = self.tables[table_id - 1]
        print(f"🍽️  ORDER #{order['id']}: Table {table_id} - Customer wants food!")
    
    def assign_orders_to_robots(self):
        """Assign waiting orders to available robots"""
        for order in self.waiting_orders:
            if order['status'] == 'WAITING':
                # Find idle robot
                for robot_name, robot_info in self.robots.items():
                    if robot_info['status'] == 'IDLE' and robot_info['assigned_order'] is None:
                        # Assign order
                        order['status'] = 'ASSIGNED'
                        order['assigned_robot'] = robot_name
                        robot_info['status'] = 'ASSIGNED'
                        robot_info['assigned_order'] = order['id']
                        
                        table = self.tables[order['table_id'] - 1]
                        print(f"🤖 {robot_name.upper()} assigned Order #{order['id']} → Table {order['table_id']}")
                        break
    
    def check_order_completion(self):
        """Check if orders have been delivered"""
        completed_orders = []
        
        for order in self.waiting_orders:
            if order['status'] == 'ASSIGNED':
                table = self.tables[order['table_id'] - 1]
                
                # Simple check: if enough time passed, mark as delivered
                # In real implementation, robot would send completion message
                if self.supervisor.getTime() - order['created_time'] > 20:
                    order['status'] = 'DELIVERED'
                    table['has_food'] = True
                    self.total_deliveries += 1
                    
                    # Free up robot
                    robot_name = order['assigned_robot']
                    if robot_name:
                        self.robots[robot_name]['status'] = 'IDLE'
                        self.robots[robot_name]['assigned_order'] = None
                    
                    print(f"✨ ORDER #{order['id']} DELIVERED to Table {order['table_id']}! (Total: {self.total_deliveries})")
                    completed_orders.append(order)
                    
                    # Customer satisfied, might leave later
                    # (simplified - in full version, customers would leave after eating)
        
        # Remove completed orders
        for order in completed_orders:
            self.waiting_orders.remove(order)
    
    def print_statistics(self):
        """Print current restaurant statistics"""
        if int(self.supervisor.getTime()) % 10 == 0:  # Every 10 seconds
            occupied = sum(1 for t in self.tables if t['occupied'])
            idle_robots = sum(1 for r in self.robots.values() if r['status'] == 'IDLE')
            
            print(f"\n📊 === RESTAURANT STATUS ===")
            print(f"   👥 Active Customers: {len(self.active_customers)}")
            print(f"   🪑 Tables Occupied: {occupied}/11")
            print(f"   📝 Pending Orders: {len(self.waiting_orders)}")
            print(f"   🤖 Idle Robots: {idle_robots}/3")
            print(f"   ✅ Total Deliveries: {self.total_deliveries}")
            print(f"   ⏱️  Simulation Time: {int(self.supervisor.getTime())}s\n")
    
    def run(self):
        """Main supervisor loop"""
        while self.supervisor.step(self.timestep) != -1:
            current_time = self.supervisor.getTime() * 1000  # ms
            
            # Spawn customers periodically
            if current_time - self.last_spawn_time > self.customer_spawn_interval:
                if len(self.active_customers) < 11:  # Max = # of tables
                    self.spawn_customer()
                    self.last_spawn_time = current_time
            
            # Update customer positions
            self.update_customers()
            
            # Assign orders to robots
            self.assign_orders_to_robots()
            
            # Check for completed deliveries
            self.check_order_completion()
            
            # Print statistics
            # self.print_statistics()  # Uncomment for periodic stats

if __name__ == "__main__":
    supervisor = RestaurantSupervisor()
    supervisor.run()
