import math


class ForceDirectGraph:
    def __init__(self, positions, edges, max_iterations, repulsion_const=5000, damping_const=0.85,
                 attraction_constant=0.1):
        self.current_iteration = 0
        self.max_iterations = max_iterations
        self.positions = positions
        self.edges = edges
        self.repulsion_const = repulsion_const
        self.damping_const = damping_const
        self.attraction_constant = attraction_constant

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_iteration < self.max_iterations:
            self.current_iteration += 1
            forces = self._calculate_forces()
            return self._update_positions(forces)
        else:
            raise StopIteration

    def _calculate_forces(self):
        nodes = self.positions.keys()
        forces = {node_id: [0, 0] for node_id in nodes}

        # repulsive forces between all nodes
        for i, node_1 in enumerate(nodes):
            for j, node_2 in enumerate(nodes):
                if i >= j:
                    continue

                x1, y1 = self.positions[node_1]
                x2, y2 = self.positions[node_2]
                dx, dy = x2 - x1, y2 - y1
                distance = math.sqrt(dx ** 2 + dy ** 2) + 0.1
                force = self.repulsion_const / (distance ** 2)
                fx, fy = force * dx / distance, force * dy / distance
                forces[node_1][0] -= fx
                forces[node_1][1] -= fy
                forces[node_2][0] += fx
                forces[node_2][1] += fy

        # attractive forces for connected nodes
        for node_1, node_2 in self.edges:
            x1, y1 = self.positions[node_1]
            x2, y2 = self.positions[node_2]
            dx, dy = x2 - x1, y2 - y1
            distance = math.sqrt(dx ** 2 + dy ** 2) + 0.1
            force = self.attraction_constant * distance
            fx, fy = force * dx / distance, force * dy / distance
            forces[node_1][0] += fx
            forces[node_1][1] += fy
            forces[node_2][0] -= fx
            forces[node_2][1] -= fy

        return forces

    def _update_positions(self, forces):
        nodes = self.positions.keys()

        for node_id in nodes:
            fx, fy = forces[node_id]
            x, y = self.positions[node_id]
            self.positions[node_id] = [x + self.damping_const * fx, y + self.damping_const * fy]

        return self.positions
