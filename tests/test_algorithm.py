import unittest

from algorithm import ForceDirectGraph


class TestForceDirectGraph(unittest.TestCase):

    def setUp(self):
        # Setup some sample data for the test
        self.positions = {
            1: [0, 0],
            2: [1, 0],
            3: [0, 1],
            4: [1, 1]
        }
        self.edges = [(1, 2), (2, 3), (3, 4), (4, 1)]  # Creating a square graph
        self.max_iterations = 10
        self.graph = ForceDirectGraph(self.positions, self.edges, self.max_iterations)

    def test_initialization(self):
        # Test if the graph is initialized correctly
        self.assertEqual(self.graph.positions, self.positions)
        self.assertEqual(self.graph.edges, self.edges)
        self.assertEqual(self.graph.max_iterations, self.max_iterations)
        self.assertEqual(self.graph.repulsion_const, 5000)
        self.assertEqual(self.graph.damping_const, 0.85)
        self.assertEqual(self.graph.attraction_constant, 0.1)

    def test_iteration(self):
        # Test iteration logic (i.e. running through the maximum iterations)
        iteration_count = 0

        for new_positions in self.graph:
            iteration_count += 1
            self.assertIsInstance(new_positions, dict)
            self.assertEqual(len(new_positions),
                             len(self.positions))  # Same number of positions should be returned each time

        self.assertEqual(iteration_count, self.max_iterations)  # Should run max_iterations times


if __name__ == "__main__":
    unittest.main()
