"""
Restaurant Supervisor - Manages customers, food, and robot delivery detection.
- Spawns walking customers from door to tables
- Detects robot deliveries via customData field
- Spawns food on tables when delivered
- 80s eating timer -> customers leave -> food disappears -> new customers
"""

from controller import Supervisor
import random
import math


class RestaurantSupervisor:
    def __init__(self):
        self.sup = Supervisor()
        self.dt_ms = int(self.sup.getBasicTimeStep())
        self.dt = self.dt_ms / 1000.0

        # ---- Table definitions ----
        self.tables = {
            1:  {'pos': (-7,  7), 'chairs': [(-6.3, 7, 0.45, 3.14159), (-7.7, 7, 0.45, 0)]},
            2:  {'pos': (-7,  4), 'chairs': [(-6.3, 4, 0.45, 3.14159), (-7.7, 4, 0.45, 0)]},
            3:  {'pos': (-7,  1), 'chairs': [(-6.3, 1, 0.45, 3.14159), (-7.7, 1, 0.45, 0)]},
            4:  {'pos': (-7, -2), 'chairs': [(-6.3,-2, 0.45, 3.14159), (-7.7,-2, 0.45, 0)]},
            5:  {'pos': (-7, -5), 'chairs': [(-6.3,-5, 0.45, 3.14159), (-7.7,-5, 0.45, 0)]},
            6:  {'pos': (-2,  6), 'chairs': [(-1.3, 6, 0.45, 3.14159), (-2.7, 6, 0.45, 0),
                                              (-2, 6.7, 0.45, -1.5708), (-2, 5.3, 0.45, 1.5708)]},
            7:  {'pos': (-2,  2), 'chairs': [(-1.3, 2, 0.45, 3.14159), (-2.7, 2, 0.45, 0),
                                              (-2, 2.7, 0.45, -1.5708), (-2, 1.3, 0.45, 1.5708)]},
            8:  {'pos': (-2, -2), 'chairs': [(-1.3,-2, 0.45, 3.14159), (-2.7,-2, 0.45, 0),
                                              (-2,-1.3, 0.45, -1.5708), (-2,-2.7, 0.45, 1.5708)]},
            9:  {'pos': (2,   6), 'chairs': [(2.7, 6, 0.45, 3.14159), (1.3, 6, 0.45, 0)]},
            10: {'pos': (2,   2), 'chairs': [(2.7, 2, 0.45, 3.14159), (1.3, 2, 0.45, 0)]},
            11: {'pos': (2,  -2), 'chairs': [(2.7,-2, 0.45, 3.14159), (1.3,-2, 0.45, 0)]},
        }

        self.shirt_colors = [
            (0.2,0.4,0.8), (0.8,0.2,0.4), (0.4,0.8,0.2),
            (0.8,0.6,0.2), (0.6,0.2,0.8), (0.2,0.8,0.8),
            (0.8,0.4,0.6), (0.3,0.3,0.7), (0.7,0.5,0.3),
        ]
        self.skin_tones = [
            (0.95,0.76,0.65), (0.82,0.62,0.48),
            (0.65,0.45,0.35), (0.48,0.36,0.27),
        ]

        # State tracking
        self.table_state = {}       # 'empty'|'waiting'|'eating'|'leaving'
        self.table_food = {}        # list of food/plate nodes
        self.table_customers = {}   # list of customer dicts
        self.table_eat_start = {}   # when eating started
        self.chair_taken = {}       # (tid, chair_idx) -> bool

        for tid in self.tables:
            self.table_state[tid] = 'empty'
            self.table_food[tid] = []
            self.table_customers[tid] = []
            for ci in range(len(self.tables[tid]['chairs'])):
                self.chair_taken[(tid, ci)] = False

        # Walking customers
        self.walkers = []
        self.total_spawned = 0
        self.walk_speed = 4.0

        # Robot delivery detection
        self._robot_nodes = {}
        self._last_data = {}

        self.EATING_TIME = 80.0
        self.step_n = 0

        print("=" * 50)
        print("  RESTAURANT SUPERVISOR")
        print(f"  Eating time: {self.EATING_TIME}s")
        print("=" * 50)

    # ---- Node import helper ----
    def _import(self, vrml):
        root = self.sup.getRoot()
        ch = root.getField('children')
        ch.importMFNodeFromString(-1, vrml.strip())
        return ch.getMFNode(ch.getCount() - 1)

    # ---- Find robot nodes (called once) ----
    def _find_robots(self):
        root = self.sup.getRoot()
        ch = root.getField('children')
        for i in range(ch.getCount()):
            node = ch.getMFNode(i)
            if node is None:
                continue
            nf = node.getField('name')
            if nf is None:
                continue
            name = nf.getSFString()
            if name.startswith('service_robot_'):
                try:
                    rid = int(name.split('_')[-1])
                    self._robot_nodes[rid] = node
                except ValueError:
                    pass
        print(f"  Found {len(self._robot_nodes)} robots: {list(self._robot_nodes.keys())}")

    # ---- Pathfinding ----
    def _path_to_chair(self, door_x, door_y, cx, cy, tid):
        LEFT = -4.5; CENTER = 0.0; RIGHT = 4.5; ENTRY_Y = -7.5
        tx = self.tables[tid]['pos'][0]
        entry = (door_x, ENTRY_Y)
        if tid <= 5:
            ax = LEFT
        elif tid <= 8:
            ax = CENTER if cx > tx else LEFT
        else:
            ax = RIGHT if cx > tx else CENTER
        return [entry, (ax, ENTRY_Y), (ax, cy), (cx, cy)]

    def _path_to_door(self, cx, cy, tid):
        LEFT = -4.5; CENTER = 0.0; RIGHT = 4.5; EXIT_Y = -7.5
        dx = random.uniform(-2, 2)
        if tid <= 5: ax = LEFT
        elif tid <= 8: ax = CENTER
        else: ax = RIGHT
        return [(ax, cy), (ax, EXIT_Y), (dx, EXIT_Y), (dx, -9.5)]

    # ---- Standing humanoid ----
    def _spawn_standing(self, cid, x, y, skin, shirt):
        s, sk = shirt, skin
        p = (s[0]*0.3, s[1]*0.3, s[2]*0.3)
        vrml = f"""DEF {cid} Solid {{
  translation {x} {y} 0
  rotation 0 0 1 1.5708
  children [
    Transform {{ translation 0 0 1.65
      children [ Shape {{ appearance PBRAppearance {{ baseColor {sk[0]} {sk[1]} {sk[2]} roughness 0.7 metalness 0.05 }} geometry Sphere {{ radius 0.1 subdivision 2 }} }} ] }}
    Transform {{ translation 0 0 1.52
      children [ Shape {{ appearance PBRAppearance {{ baseColor {sk[0]} {sk[1]} {sk[2]} roughness 0.7 }} geometry Cylinder {{ height 0.06 radius 0.035 }} }} ] }}
    Transform {{ translation 0 0 1.3
      children [ Shape {{ appearance PBRAppearance {{ baseColor {s[0]} {s[1]} {s[2]} roughness 0.85 }} geometry Box {{ size 0.24 0.18 0.35 }} }} ] }}
    Transform {{ translation 0 0.13 1.3
      children [ Shape {{ appearance PBRAppearance {{ baseColor {s[0]} {s[1]} {s[2]} roughness 0.85 }} geometry Cylinder {{ height 0.35 radius 0.035 }} }} ] }}
    Transform {{ translation 0 -0.13 1.3
      children [ Shape {{ appearance PBRAppearance {{ baseColor {s[0]} {s[1]} {s[2]} roughness 0.85 }} geometry Cylinder {{ height 0.35 radius 0.035 }} }} ] }}
    Transform {{ translation 0 0 1.08
      children [ Shape {{ appearance PBRAppearance {{ baseColor {p[0]} {p[1]} {p[2]} roughness 0.9 }} geometry Box {{ size 0.22 0.16 0.1 }} }} ] }}
    Transform {{ translation 0 0.055 0.75
      children [ Shape {{ appearance PBRAppearance {{ baseColor {p[0]} {p[1]} {p[2]} roughness 0.9 }} geometry Cylinder {{ height 0.55 radius 0.05 }} }} ] }}
    Transform {{ translation 0 -0.055 0.75
      children [ Shape {{ appearance PBRAppearance {{ baseColor {p[0]} {p[1]} {p[2]} roughness 0.9 }} geometry Cylinder {{ height 0.55 radius 0.05 }} }} ] }}
    Transform {{ translation 0.04 0.055 0.46
      children [ Shape {{ appearance PBRAppearance {{ baseColor 0.15 0.15 0.15 roughness 0.95 }} geometry Box {{ size 0.16 0.08 0.05 }} }} ] }}
    Transform {{ translation 0.04 -0.055 0.46
      children [ Shape {{ appearance PBRAppearance {{ baseColor 0.15 0.15 0.15 roughness 0.95 }} geometry Box {{ size 0.16 0.08 0.05 }} }} ] }}
  ]
  name "{cid}"
  boundingObject Box {{ size 0.3 0.2 1.7 }}
}}"""
        return self._import(vrml)

    # ---- Seated humanoid ----
    def _spawn_seated(self, cid, x, y, z, rot, skin, shirt):
        s, sk = shirt, skin
        p = (s[0]*0.3, s[1]*0.3, s[2]*0.3)
        vrml = f"""DEF {cid} Solid {{
  translation {x} {y} {z}
  rotation 0 0 1 {rot}
  children [
    Transform {{ translation 0 0 0.35
      children [ Shape {{ appearance PBRAppearance {{ baseColor {sk[0]} {sk[1]} {sk[2]} roughness 0.7 metalness 0.05 }} geometry Sphere {{ radius 0.1 subdivision 2 }} }} ] }}
    Transform {{ translation 0 0 0.26
      children [ Shape {{ appearance PBRAppearance {{ baseColor {sk[0]} {sk[1]} {sk[2]} roughness 0.7 }} geometry Cylinder {{ height 0.06 radius 0.035 }} }} ] }}
    Transform {{ translation 0 0 0.15 rotation 1 0 0 0.15
      children [ Shape {{ appearance PBRAppearance {{ baseColor {s[0]} {s[1]} {s[2]} roughness 0.85 }} geometry Box {{ size 0.24 0.18 0.3 }} }} ] }}
    Transform {{ translation 0.1 0.11 0.2 rotation 1 0 0 1.5708
      children [ Shape {{ appearance PBRAppearance {{ baseColor {s[0]} {s[1]} {s[2]} roughness 0.85 }} geometry Cylinder {{ height 0.22 radius 0.03 }} }} ] }}
    Transform {{ translation 0.1 -0.11 0.2 rotation 1 0 0 1.5708
      children [ Shape {{ appearance PBRAppearance {{ baseColor {s[0]} {s[1]} {s[2]} roughness 0.85 }} geometry Cylinder {{ height 0.22 radius 0.03 }} }} ] }}
    Transform {{
      children [ Shape {{ appearance PBRAppearance {{ baseColor {p[0]} {p[1]} {p[2]} roughness 0.9 }} geometry Box {{ size 0.22 0.16 0.08 }} }} ] }}
    Transform {{ translation -0.05 0.055 -0.1 rotation 1 0 0 1.5708
      children [ Shape {{ appearance PBRAppearance {{ baseColor {p[0]} {p[1]} {p[2]} roughness 0.9 }} geometry Cylinder {{ height 0.22 radius 0.045 }} }} ] }}
    Transform {{ translation -0.05 -0.055 -0.1 rotation 1 0 0 1.5708
      children [ Shape {{ appearance PBRAppearance {{ baseColor {p[0]} {p[1]} {p[2]} roughness 0.9 }} geometry Cylinder {{ height 0.22 radius 0.045 }} }} ] }}
    Transform {{ translation -0.05 0.055 -0.32
      children [ Shape {{ appearance PBRAppearance {{ baseColor {p[0]} {p[1]} {p[2]} roughness 0.9 }} geometry Cylinder {{ height 0.25 radius 0.04 }} }} ] }}
    Transform {{ translation -0.05 -0.055 -0.32
      children [ Shape {{ appearance PBRAppearance {{ baseColor {p[0]} {p[1]} {p[2]} roughness 0.9 }} geometry Cylinder {{ height 0.25 radius 0.04 }} }} ] }}
    Transform {{ translation 0.03 0.055 -0.45
      children [ Shape {{ appearance PBRAppearance {{ baseColor 0.15 0.15 0.15 roughness 0.95 }} geometry Box {{ size 0.15 0.07 0.05 }} }} ] }}
    Transform {{ translation 0.03 -0.055 -0.45
      children [ Shape {{ appearance PBRAppearance {{ baseColor 0.15 0.15 0.15 roughness 0.95 }} geometry Box {{ size 0.15 0.07 0.05 }} }} ] }}
  ]
  name "{cid}"
  boundingObject Box {{ size 0.3 0.2 0.8 }}
}}"""
        self._import(vrml)

    # ---- Food management ----
    def _spawn_food(self, tid):
        tx, ty = self.tables[tid]['pos']
        color = random.choice([(0.85,0.25,0.15),(0.3,0.7,0.2),(0.6,0.35,0.2),(0.9,0.8,0.3)])
        plate = self._import(f"""Solid {{
  translation {tx} {ty} 0.76
  children [ Shape {{ appearance PBRAppearance {{ baseColor 0.95 0.95 0.95 roughness 0.3 }} geometry Cylinder {{ height 0.02 radius 0.12 }} }} ]
  name "plate_t{tid}"
}}""")
        food = self._import(f"""Solid {{
  translation {tx} {ty} 0.8
  children [ Shape {{ appearance PBRAppearance {{ baseColor {color[0]} {color[1]} {color[2]} roughness 0.7 }} geometry Sphere {{ radius 0.06 }} }} ]
  name "food_t{tid}"
}}""")
        self.table_food[tid] = [plate, food]

    def _remove_food(self, tid):
        for n in self.table_food.get(tid, []):
            if n is not None:
                try:
                    n.remove()
                except Exception:
                    pass
        self.table_food[tid] = []

    # ---- Customer lifecycle ----
    def _fill_table(self, tid):
        chairs = self.tables[tid]['chairs']
        free = [i for i in range(len(chairs)) if not self.chair_taken[(tid, i)]]
        if not free:
            return
        count = min(len(free), random.randint(1, 2))

        for ci in free[:count]:
            cx, cy, cz, crot = chairs[ci]
            self.chair_taken[(tid, ci)] = True
            self.total_spawned += 1
            cid = f"cust_{self.total_spawned}"
            skin = random.choice(self.skin_tones)
            shirt = random.choice(self.shirt_colors)

            dx = random.uniform(-2, 2)
            dy = -9.0
            node = self._spawn_standing(cid, dx, dy, skin, shirt)
            if node is None:
                self.chair_taken[(tid, ci)] = False
                continue

            path = self._path_to_chair(dx, dy, cx, cy, tid)
            walker = {
                'id': cid, 'node': node, 'skin': skin, 'shirt': shirt,
                'tid': tid, 'ci': ci, 'cx': cx, 'cy': cy, 'cz': cz, 'crot': crot,
                'status': 'WALK_IN', 'x': dx, 'y': dy,
                'path': path, 'pi': 0,
            }
            self.walkers.append(walker)
            self.table_customers[tid].append(walker)

        self.table_state[tid] = 'waiting'
        print(f"  [Table {tid}] {count} customers walking in")

    def _start_leaving(self, tid):
        self._remove_food(tid)
        for w in self.table_customers[tid]:
            if w['status'] != 'SEATED':
                continue
            # Remove seated node
            seated = self.sup.getFromDef(w['id'])
            if seated:
                try:
                    seated.remove()
                except Exception:
                    pass
            # Create standing walker heading to door
            out_id = w['id'] + '_out'
            cx, cy = w['cx'], w['cy']
            node = self._spawn_standing(out_id, cx, cy, w['skin'], w['shirt'])
            if node:
                path = self._path_to_door(cx, cy, tid)
                out_w = {
                    'id': out_id, 'node': node, 'skin': w['skin'], 'shirt': w['shirt'],
                    'tid': tid, 'ci': w['ci'],
                    'status': 'WALK_OUT', 'x': cx, 'y': cy,
                    'path': path, 'pi': 0,
                }
                self.walkers.append(out_w)
            self.chair_taken[(tid, w['ci'])] = False
            w['status'] = 'GONE'

        self.table_customers[tid] = []
        self.table_state[tid] = 'leaving'
        print(f"  [Table {tid}] Customers leaving, food cleared")

    # ---- Move walkers ----
    def _move_walkers(self):
        for w in self.walkers:
            if w['status'] not in ('WALK_IN', 'WALK_OUT'):
                continue
            if w['node'] is None:
                continue

            if w['pi'] >= len(w['path']):
                # Arrived
                if w['status'] == 'WALK_IN':
                    w['node'].remove()
                    w['node'] = None
                    self._spawn_seated(w['id'], w['cx'], w['cy'], w['cz'], w['crot'],
                                       w['skin'], w['shirt'])
                    w['status'] = 'SEATED'
                    print(f"  {w['id']} seated at Table {w['tid']}")
                elif w['status'] == 'WALK_OUT':
                    w['node'].remove()
                    w['node'] = None
                    w['status'] = 'GONE'
                    # Check if all walkers for this table are gone
                    tid = w['tid']
                    all_gone = all(
                        ww['status'] == 'GONE'
                        for ww in self.walkers
                        if ww['tid'] == tid and '_out' in ww['id']
                    )
                    if all_gone and self.table_state.get(tid) == 'leaving':
                        self.table_state[tid] = 'empty'
                        print(f"  [Table {tid}] Now empty, ready for new customers")
                continue

            tx, ty = w['path'][w['pi']]
            dx, dy = tx - w['x'], ty - w['y']
            dist = math.sqrt(dx*dx + dy*dy)

            if dist < 0.2:
                w['pi'] += 1
                w['x'], w['y'] = tx, ty
                w['node'].getField('translation').setSFVec3f([tx, ty, 0])
            else:
                step = self.walk_speed * self.dt
                nx = w['x'] + (dx/dist) * step
                ny = w['y'] + (dy/dist) * step
                w['node'].getField('translation').setSFVec3f([nx, ny, 0])
                w['node'].getField('rotation').setSFRotation([0, 0, 1, math.atan2(dy, dx)])
                w['x'], w['y'] = nx, ny

    # ---- Check robot deliveries ----
    def _check_deliveries(self):
        if not self._robot_nodes:
            self._find_robots()

        for rid, node in self._robot_nodes.items():
            try:
                df = node.getField('customData')
                if df is None:
                    continue
                data = df.getSFString()
            except Exception:
                continue

            if not data or 'delivered=' not in data:
                continue

            # Skip if we already processed this exact data string
            if self._last_data.get(rid) == data:
                continue
            self._last_data[rid] = data

            # Parse table id
            try:
                tid = int(data.split('delivered=')[1].split()[0])
            except (ValueError, IndexError):
                continue

            if self.table_state.get(tid) == 'waiting':
                self.table_state[tid] = 'eating'
                self.table_eat_start[tid] = self.sup.getTime()
                self._spawn_food(tid)
                print(f"  [Table {tid}] FOOD DELIVERED by Robot {rid}! "
                      f"Eating for {self.EATING_TIME:.0f}s")

    # ---- Check eating timers ----
    def _check_eating(self):
        now = self.sup.getTime()
        for tid, state in list(self.table_state.items()):
            if state == 'eating':
                elapsed = now - self.table_eat_start.get(tid, now)
                if elapsed >= self.EATING_TIME:
                    print(f"  [Table {tid}] Done eating ({elapsed:.0f}s)")
                    self._start_leaving(tid)

    # ---- Main loop ----
    def run(self):
        print("\n  Restaurant open!\n")
        fill_idx = 0
        fill_done = False

        while self.sup.step(self.dt_ms) != -1:
            self.step_n += 1
            t = self.sup.getTime()

            # Stagger initial fills (one table per second)
            if not fill_done:
                if t >= fill_idx * 1.0 and fill_idx < len(self.tables):
                    tid = list(self.tables.keys())[fill_idx]
                    if self.table_state[tid] == 'empty':
                        self._fill_table(tid)
                    fill_idx += 1
                if fill_idx >= len(self.tables):
                    fill_done = True
                    print("\n  All tables filled!\n")

            # Check deliveries and eating (every 10 steps)
            if self.step_n % 10 == 0:
                self._check_deliveries()
                self._check_eating()

            # Refill empty tables
            if fill_done:
                for tid in self.tables:
                    if self.table_state[tid] == 'empty':
                        self._fill_table(tid)

            # Move walking customers
            self._move_walkers()


if __name__ == "__main__":
    sup = RestaurantSupervisor()
    sup.run()
