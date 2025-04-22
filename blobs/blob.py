import random
import math
from constants import TRAITS
from communities.community import Community

class Blob:
    """
    Autonomous agent with randomized personality traits.
    Movement based on similarity to others.
    Community selection, social actions, and leadership dynamics.
    """

    def __init__(self, id, position, movement_unit=5, grid_size=50):
        self.id = id
        # store as list so we can mutate components
        self.position = [float(position[0]), float(position[1])]
        self.movement_unit = movement_unit
        self.grid_size = grid_size
        self.community = None

        # Traits: define personality and behavior characteristics
        self.traits = {
            'curiosity': random.random(),
            'empathy': random.random(),
            'charisma': random.random(),
            'caution': random.random(),
            'intelligence': random.random(),
            'strength': random.random(),
            'health': random.random(),
            'aggression': random.random(),
            'loyalty': random.random(),
            'resilience': random.random(),
        }

    def similarity(self, other):
        dist_sq = sum((self.traits[t] - other.traits[t])**2 for t in TRAITS)
        return -math.sqrt(dist_sq)

    def decide_move(self, blobs, region_centers):
        """
        Move under two influences:
          - community pull: toward your most-similar blob
          - region pull: toward the center of your dominant-trait stripe
        """
        if len(blobs) <= 1:
            return

        # --- 1) Community pull ------------------------------------------------
        best_blob = None
        best_sim = -float('inf')
        for b in blobs:
            if b.id == self.id:
                continue
            sim = -math.sqrt(sum((self.traits[t] - b.traits[t])**2 for t in TRAITS))
            if sim > best_sim:
                best_sim, best_blob = sim, b

        if not best_blob:
            return

        # vector toward most‐similar blob
        dx_c = best_blob.position[0] - self.position[0]
        dy_c = best_blob.position[1] - self.position[1]
        dist_c = math.hypot(dx_c, dy_c) or 1e-6
        vx_c, vy_c = dx_c/dist_c, dy_c/dist_c

        # --- 2) Region pull ---------------------------------------------------
        # pick the trait region corresponding to this blob's highest of the four
        region_traits = list(region_centers.keys())
        # find dominant among those four
        dom = max(region_traits, key=lambda tr: self.traits.get(tr, 0))
        cx, cy = region_centers[dom]
        dx_r = cx - self.position[0]
        dy_r = cy - self.position[1]
        dist_r = math.hypot(dx_r, dy_r) or 1e-6
        vx_r, vy_r = dx_r/dist_r, dy_r/dist_r

        # --- 3) Combine & Step ------------------------------------------------
        w_c, w_r = 0.5, 0.5  # weights for community vs region
        vx = vx_c * w_c + vx_r * w_r
        vy = vy_c * w_c + vy_r * w_r
        norm = math.hypot(vx, vy) or 1e-6
        vx, vy = vx/norm, vy/norm

        # move
        step = self.movement_unit
        new_x = self.position[0] + vx*step
        new_y = self.position[1] + vy*step

        # clamp inside [0, grid_size)
        new_x = min(max(0, new_x), self.grid_size-1)
        new_y = min(max(0, new_y), self.grid_size-1)

        self.position = [new_x, new_y]
        print(
            f"Blob {self.id} → moved (sim={best_sim:.3f}) "
            f"toward Blob {best_blob.id} & into '{dom}' stripe: "
            f"new pos=({new_x:.1f},{new_y:.1f})"
        )

    def evaluate_community(self, communities):
        def similarity_to_community(community):
            return sum(self.traits[trait] for trait in community.core_traits) / len(community.core_traits)

        best_fit = None
        best_score = 0.0
        threshold = 0.6

        for community in communities:
            score = similarity_to_community(community)
            print(f"Blob {self.id} evaluates community '{community.name}' with similarity score {score:.2f}")
            if score > best_score:
                best_fit = community
                best_score = score

        if best_score >= threshold:
            print(f"Blob {self.id} joins community '{best_fit.name}'")
            best_fit.add_member(self)
        else:
            sorted_traits = sorted(self.traits.items(), key=lambda x: x[1], reverse=True)
            new_core_traits = [t for t, v in sorted_traits[:3]]
            new_name = f"Neo-{self.id}"
            new_community = Community(new_name, new_core_traits)
            new_community.add_member(self)
            communities.append(new_community)
            print(f"Blob {self.id} creates a new community '{new_name}' with core traits {new_core_traits}")

    def get_nearby_blobs(self, blobs, radius=5):
        return [
            b for b in blobs
            if b.id != self.id and
               math.hypot(self.position[0] - b.position[0], self.position[1] - b.position[1]) <= radius
        ]

    def act(self, world):
        nearby_blobs = self.get_nearby_blobs(world['blobs'], radius=5)
        for other in nearby_blobs:
            print(f"Blob {self.id} chats with Blob {other.id}")

        if self.community and (self.community.leader is None or self.community.leader.id != self.id):
            score = (
                self.traits['charisma']
                + self.traits['intelligence']
                + self.traits['strength']
            )
            current_leader_score = (
                sum(self.community.leader.traits[t] for t in ['charisma', 'intelligence', 'strength'])
                if self.community.leader else 0
            )
            if score > current_leader_score + 0.2:
                print(f"Blob {self.id} challenges leadership in '{self.community.name}'")
                self.community.leader = self
                print(f"Blob {self.id} is now leader of '{self.community.name}'!")

        if self.community:
            core_fit = sum(self.traits[t] for t in self.community.core_traits) / len(self.community.core_traits)
            if core_fit < 0.3:
                print(f"Blob {self.id} feels out of place in '{self.community.name}' and leaves.")
                self.community.remove_member(self)
                self.community = None
