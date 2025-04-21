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

    def decide_move(self, blobs):
        """
        If there's a sufficiently similar blob, move toward it.
        Otherwise, move away from the most dissimilar blob.
        """
        if len(blobs) <= 1:
            return

        best_blob = None
        worst_blob = None
        best_sim = float('-inf')
        worst_sim = float('inf')
        for b in blobs:
            if b.id == self.id:
                continue
            sim = self.similarity(b)
            if sim > best_sim:
                best_sim, best_blob = sim, b
            if sim < worst_sim:
                worst_sim, worst_blob = sim, b

        # threshold for "similar enough" (tweakable)
        threshold = -1.0

        if best_sim >= threshold:
            # move toward the most similar blob
            target = best_blob
            direction = (
                target.position[0] - self.position[0],
                target.position[1] - self.position[1]
            )
        else:
            # move away from the most dissimilar blob
            target = worst_blob
            direction = (
                self.position[0] - target.position[0],
                self.position[1] - target.position[1]
            )

        dx, dy = direction
        dist = math.hypot(dx, dy)
        if dist < 1e-6:
            return  # no meaningful direction

        # normalize and apply movement (faster when fleeing)
        speed = self.movement_unit if best_sim >= threshold else self.movement_unit * 1.5
        step_x = (dx / dist) * speed
        step_y = (dy / dist) * speed

        # clamp within bounds
        new_x = min(max(0, self.position[0] + step_x), self.grid_size - 1)
        new_y = min(max(0, self.position[1] + step_y), self.grid_size - 1)

        self.position = [new_x, new_y]
        action = "towards" if best_sim >= threshold else "away from"
        print(f"Blob {self.id} moved {action} Blob {target.id} → "
              f"new position: ({new_x:.2f}, {new_y:.2f}) (sim={best_sim:.3f})")

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
