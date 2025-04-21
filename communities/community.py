from constants import TRAITS

class Community:
    """
    Group of blobs sharing core traits and behaviors.
    """
    def __init__(self, name, core_traits):
        self.name = name
        self.core_traits = core_traits  # list of trait names
        self.members = []
        self.leader = None

    def add_member(self, blob):
        if blob not in self.members:
            self.members.append(blob)
            blob.community = self
            print(f"Blob {blob.id} added to community '{self.name}'")

    def remove_member(self, blob):
        if blob in self.members:
            self.members.remove(blob)
            blob.community = None
            print(f"Blob {blob.id} removed from community '{self.name}'")

    def evaluate_leadership(self):
        """
        Choose a leader based on highest sum of leadership traits.
        """
        if not self.members:
            self.leader = None
            return
        best = None
        best_score = -1
        for b in self.members:
            score = b.traits.get('charisma', 0) + b.traits.get('intelligence', 0) + b.traits.get('strength', 0)
            if score > best_score:
                best = b
                best_score = score
        if best and self.leader != best:
            self.leader = best
            print(f"Blob {best.id} is now leader of '{self.name}' (score={best_score:.2f})")

    def evolve(self):
        """
        Update core_traits based on average member traits.
        """
        if not self.members:
            return
        trait_sums = {trait: 0.0 for trait in TRAITS}
        for b in self.members:
            for trait, value in b.traits.items():
                trait_sums[trait] = trait_sums.get(trait, 0.0) + value
        trait_avgs = {trait: trait_sums[trait] / len(self.members) for trait in trait_sums}
        new_traits = sorted(trait_avgs, key=lambda t: trait_avgs[t], reverse=True)[:3]
        if set(new_traits) != set(self.core_traits):
            old = self.core_traits
            self.core_traits = new_traits
            print(f"Community '{self.name}' core traits evolved from {old} to {new_traits}")
