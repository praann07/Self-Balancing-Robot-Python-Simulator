"""
🏪 Clean Restaurant Supervisor Controller
Spawns realistic humanoid customers seated at tables

Step-by-step approach:
1. Build clean environment ✓
2. Spawn humanoid customers properly seated
3. No movement - just realistic seated people
"""

from controller import Supervisor
import random
import time

class RestaurantSupervisor:
    def __init__(self):
        self.supervisor = Supervisor()
        self.timestep = int(self.supervisor.getBasicTimeStep())
        
        # Table information with chair positions for seated customers
        self.tables = [
            {'id': 1, 'pos': (-7, 7, 0.45), 'chair_pos': [(-6.3, 7, 0.45), (-7.7, 7, 0.45)], 'rotation': [-1.5708, 1.5708], 'occupied': False},
            {'id': 2, 'pos': (-7, 4, 0.45), 'chair_pos': [(-6.3, 4, 0.45), (-7.7, 4, 0.45)], 'rotation': [-1.5708, 1.5708], 'occupied': False},
            {'id': 3, 'pos': (-7, 1, 0.45), 'chair_pos': [(-6.3, 1, 0.45), (-7.7, 1, 0.45)], 'rotation': [-1.5708, 1.5708], 'occupied': False},
            {'id': 4, 'pos': (-7, -2, 0.45), 'chair_pos': [(-6.3, -2, 0.45), (-7.7, -2, 0.45)], 'rotation': [-1.5708, 1.5708], 'occupied': False},
            {'id': 5, 'pos': (-7, -5, 0.45), 'chair_pos': [(-6.3, -5, 0.45), (-7.7, -5, 0.45)], 'rotation': [-1.5708, 1.5708], 'occupied': False},
            {'id': 6, 'pos': (-2, 6, 0.45), 'chair_pos': [(-1.2, 6, 0.45), (-2.8, 6, 0.45), (-2, 6.8, 0.45), (-2, 5.2, 0.45)], 'rotation': [-1.5708, 1.5708, 3.14159, 0], 'occupied': False},
            {'id': 7, 'pos': (-2, 2, 0.45), 'chair_pos': [(-1.2, 2, 0.45), (-2.8, 2, 0.45), (-2, 2.8, 0.45), (-2, 1.2, 0.45)], 'rotation': [-1.5708, 1.5708, 3.14159, 0], 'occupied': False},
            {'id': 8, 'pos': (-2, -2, 0.45), 'chair_pos': [(-1.2, -2, 0.45), (-2.8, -2, 0.45), (-2, -1.2, 0.45), (-2, -2.8, 0.45)], 'rotation': [-1.5708, 1.5708, 0, 3.14159], 'occupied': False},
            {'id': 9, 'pos': (2, 6, 0.45), 'chair_pos': [(2.7, 6, 0.45), (1.3, 6, 0.45)], 'rotation': [-1.5708, 1.5708], 'occupied': False},
            {'id': 10, 'pos': (2, 2, 0.45), 'chair_pos': [(2.7, 2, 0.45), (1.3, 2, 0.45)], 'rotation': [-1.5708, 1.5708], 'occupied': False},
            {'id': 11, 'pos': (2, -2, 0.45), 'chair_pos': [(2.7, -2, 0.45), (1.3, -2, 0.45)], 'rotation': [-1.5708, 1.5708], 'occupied': False},
        ]
        
        # Customer colors (for variety and realism)
        self.customer_colors = [
            (0.2, 0.4, 0.8),  # Blue shirt
            (0.8, 0.2, 0.4),  # Red/Pink shirt
            (0.4, 0.8, 0.2),  # Green shirt
            (0.8, 0.6, 0.2),  # Orange/Yellow shirt
            (0.6, 0.2, 0.8),  # Purple shirt
            (0.2, 0.8, 0.8),  # Cyan shirt
            (0.8, 0.4, 0.6),  # Pink shirt
            (0.3, 0.3, 0.7),  # Navy shirt
            (0.7, 0.5, 0.3),  # Brown shirt
            (0.5, 0.7, 0.5),  # Light green shirt
        ]
        
        # Statistics
        self.total_customers = 0
        self.spawn_interval = 5000  # 5 seconds between spawns
        self.last_spawn_time = 0
        self.max_customers = 15  # Limit to prevent overcrowding
        
        print("╔═══════════════════════════════════════════════════════════╗")
        print("║   🏪 CLEAN RESTAURANT ENVIRONMENT - SUPERVISOR ACTIVE     ║")
        print("╠═══════════════════════════════════════════════════════════╣")
        print("║  👥 Realistic Humanoid Customers                          ║")
        print("║  🪑 Properly Seated at Tables                             ║")
        print("║  🎯 Step-by-Step Build: Environment Focus                 ║")
        print("╚═══════════════════════════════════════════════════════════╝\n")
        
    def create_seated_humanoid(self, customer_id, position, rotation_z):
        """
        Create a realistic humanoid customer in sitting posture
        
        Args:
            customer_id: Unique customer identifier
            position: (x, y, z) tuple for chair position
            rotation_z: Rotation angle to face table
        """
        x, y, z = position
        color = random.choice(self.customer_colors)
        
        # Skin tone variations
        skin_tones = [
            (0.95, 0.76, 0.65),  # Light
            (0.82, 0.62, 0.48),  # Medium
            (0.65, 0.45, 0.35),  # Tan
            (0.48, 0.36, 0.27),  # Brown
        ]
        skin = random.choice(skin_tones)
        
        # Safe color clamping to [0, 1]
        head_color = (min(skin[0], 1.0), min(skin[1], 1.0), min(skin[2], 1.0))
        shirt_color = (min(color[0], 1.0), min(color[1], 1.0), min(color[2], 1.0))
        pants_color = (color[0] * 0.3, color[1] * 0.3, color[2] * 0.3)
        
        # VRML for seated humanoid (sitting posture - legs bent, arms on table)
        customer_def = f"""
        DEF {customer_id} Solid {{
          translation {x} {y} {z}
          rotation 0 0 1 {rotation_z}
          children [
            # HEAD
            Transform {{
              translation 0 0 0.35
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {head_color[0]} {head_color[1]} {head_color[2]}
                    roughness 0.7
                    metalness 0.05
                  }}
                  geometry Sphere {{
                    radius 0.1
                    subdivision 2
                  }}
                }}
              ]
            }}
            # NECK
            Transform {{
              translation 0 0 0.26
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {head_color[0]} {head_color[1]} {head_color[2]}
                    roughness 0.7
                  }}
                  geometry Cylinder {{
                    height 0.06
                    radius 0.035
                  }}
                }}
              ]
            }}
            # TORSO (shirt) - slightly bent forward when seated
            Transform {{
              translation 0 0 0.15
              rotation 1 0 0 0.2
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {shirt_color[0]} {shirt_color[1]} {shirt_color[2]}
                    roughness 0.85
                    metalness 0.02
                  }}
                  geometry Box {{
                    size 0.24 0.18 0.3
                  }}
                }}
              ]
            }}
            # LEFT ARM (resting on table)
            Transform {{
              translation 0.08 0.11 0.2
              rotation 1 0 0 1.5708
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {shirt_color[0]} {shirt_color[1]} {shirt_color[2]}
                    roughness 0.85
                  }}
                  geometry Cylinder {{
                    height 0.25
                    radius 0.03
                  }}
                }}
              ]
            }}
            # RIGHT ARM (resting on table)
            Transform {{
              translation 0.08 -0.11 0.2
              rotation 1 0 0 1.5708
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {shirt_color[0]} {shirt_color[1]} {shirt_color[2]}
                    roughness 0.85
                  }}
                  geometry Cylinder {{
                    height 0.25
                    radius 0.03
                  }}
                }}
              ]
            }}
            # LEFT HAND
            Transform {{
              translation 0.2 0.11 0.2
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {head_color[0]} {head_color[1]} {head_color[2]}
                    roughness 0.75
                  }}
                  geometry Sphere {{
                    radius 0.04
                    subdivision 1
                  }}
                }}
              ]
            }}
            # RIGHT HAND
            Transform {{
              translation 0.2 -0.11 0.2
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {head_color[0]} {head_color[1]} {head_color[2]}
                    roughness 0.75
                  }}
                  geometry Sphere {{
                    radius 0.04
                    subdivision 1
                  }}
                }}
              ]
            }}
            # WAIST/HIPS
            Transform {{
              translation 0 0 0.02
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {pants_color[0]} {pants_color[1]} {pants_color[2]}
                    roughness 0.9
                  }}
                  geometry Box {{
                    size 0.22 0.16 0.08
                  }}
                }}
              ]
            }}
            # LEFT THIGH (bent - sitting posture)
            Transform {{
              translation -0.05 0.055 -0.08
              rotation 1 0 0 1.5708
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {pants_color[0]} {pants_color[1]} {pants_color[2]}
                    roughness 0.9
                  }}
                  geometry Cylinder {{
                    height 0.25
                    radius 0.045
                  }}
                }}
              ]
            }}
            # RIGHT THIGH (bent - sitting posture)
            Transform {{
              translation -0.05 -0.055 -0.08
              rotation 1 0 0 1.5708
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {pants_color[0]} {pants_color[1]} {pants_color[2]}
                    roughness 0.9
                  }}
                  geometry Cylinder {{
                    height 0.25
                    radius 0.045
                  }}
                }}
              ]
            }}
            # LEFT LOWER LEG (vertical - sitting)
            Transform {{
              translation -0.05 0.055 -0.32
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {pants_color[0]} {pants_color[1]} {pants_color[2]}
                    roughness 0.9
                  }}
                  geometry Cylinder {{
                    height 0.28
                    radius 0.04
                  }}
                }}
              ]
            }}
            # RIGHT LOWER LEG (vertical - sitting)
            Transform {{
              translation -0.05 -0.055 -0.32
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor {pants_color[0]} {pants_color[1]} {pants_color[2]}
                    roughness 0.9
                  }}
                  geometry Cylinder {{
                    height 0.28
                    radius 0.04
                  }}
                }}
              ]
            }}
            # LEFT FOOT
            Transform {{
              translation 0.03 0.055 -0.46
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor 0.15 0.15 0.15
                    roughness 0.95
                  }}
                  geometry Box {{
                    size 0.15 0.07 0.05
                  }}
                }}
              ]
            }}
            # RIGHT FOOT
            Transform {{
              translation 0.03 -0.055 -0.46
              children [
                Shape {{
                  appearance PBRAppearance {{
                    baseColor 0.15 0.15 0.15
                    roughness 0.95
                  }}
                  geometry Box {{
                    size 0.15 0.07 0.05
                  }}
                }}
              ]
            }}
          ]
          name "{customer_id}"
          boundingObject Box {{
            size 0.3 0.2 0.8
          }}
          physics Physics {{
            density -1
            mass 70
          }}
        }}
        """
        
        # Import customer into world
        root = self.supervisor.getRoot()
        children_field = root.getField('children')
        children_field.importMFNodeFromString(-1, customer_def)
        
        print(f"👤 Spawned {customer_id} seated at table (realistic humanoid)")
        
    def spawn_customer(self):
        """Spawn customers seated at random tables"""
        if self.total_customers >= self.max_customers:
            return
        
        # Find empty tables
        empty_tables = [t for t in self.tables if not t['occupied']]
        
        if not empty_tables:
            return
        
        # Pick random empty table
        table = random.choice(empty_tables)
        
        # Randomly select chair(s) to fill at this table
        num_chairs = len(table['chair_pos'])
        chairs_to_fill = random.randint(1, min(2, num_chairs))  # Fill 1-2 chairs max per spawn
        
        for i in range(chairs_to_fill):
            if self.total_customers >= self.max_customers:
                break
                
            chair_idx = random.randint(0, num_chairs - 1)
            chair_pos = table['chair_pos'][chair_idx]
            rotation = table['rotation'][chair_idx]
            
            customer_id = f"customer_{self.total_customers + 1}"
            self.create_seated_humanoid(customer_id, chair_pos, rotation)
            
            self.total_customers += 1
        
        table['occupied'] = True
    
    def run(self):
        """Main control loop"""
        print("\n🚀 Restaurant simulation started!")
        print("👥 Customers will spawn every 5 seconds...")
        print("🪑 All customers will be properly seated at tables\n")
        
        while self.supervisor.step(self.timestep) != -1:
            current_time = self.supervisor.getTime() * 1000  # Convert to ms
            
            # Spawn customers periodically
            if current_time - self.last_spawn_time >= self.spawn_interval:
                self.spawn_customer()
                self.last_spawn_time = current_time

if __name__ == "__main__":
    supervisor = RestaurantSupervisor()
    supervisor.run()
