import tkinter as tk
import math
import random
from algorithm import ForceDirectGraph
import time
from collections import defaultdict
from itertools import chain


class CONST:
    APP_WIDTH_PX = 1200
    APP_HEIGHT_PX = 840
    CANVAS_WIDTH_PX = APP_WIDTH_PX - 200
    CANVAS_HEIGHT_PX = APP_HEIGHT_PX - 40

    RANDOM_GRAPH_POINTS = 30
    POINT_RADIUS = 1
    EDGE_WIDTH = .5

    FDG_ITERATIONS = 50
    FDG_REPULSION_CONSTANT = 6000
    FDG_ATTRACTION_CONSTANT = 0.03
    FDG_DAMPING_CONSTANT = 1

    NODE_NON_SELECTED_COLOR = 'blue'
    NODE_SELECTED_COLOR = 'yellow'
    EDGE_COLOR = 'white'


class Graph(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nodes = {}  # node_from: [node_to, ...]
        self.selected = []  # list of node_id
        self.edges = {}  # (node_from, node_to): edge_id
        self.colors = ['#e62e2e',
                       '#e6442e',
                       '#e65a2e',
                       '#e6702e',
                       '#e6862e',
                       '#e69c2e',
                       '#e6b22e',
                       '#e6c82e',
                       '#e6de2e',
                       '#d7e62e',
                       '#c1e62e',
                       '#abe62e',
                       '#95e62e',
                       '#7fe62e',
                       '#69e62e',
                       '#53e62e',
                       '#3de62e',
                       '#2ee635',
                       '#2ee64b',
                       '#2ee661',
                       '#2ee677',
                       '#2ee68d',
                       '#2ee6a3',
                       '#2ee6b9',
                       '#2ee6cf',
                       '#2ee6e6',
                       '#2ecfe6',
                       '#2eb9e6',
                       '#2ea3e6',
                       '#2e8de6',
                       '#2e77e6',
                       '#2e61e6',
                       '#2e4be6',
                       '#2e35e6',
                       '#3d2ee6',
                       '#532ee6',
                       '#692ee6',
                       '#7f2ee6',
                       '#952ee6',
                       '#ab2ee6',
                       '#c12ee6',
                       '#d72ee6',
                       '#e62ede',
                       '#e62ec8',
                       '#e62eb2',
                       '#e62e9c',
                       '#e62e86',
                       '#e62e70',
                       '#e62e5a',
                       '#e62e44']

    def on_click(self, event):
        clicked_node = self.find_withtag("current")

        if not clicked_node:
            x0 = event.x - CONST.POINT_RADIUS
            y0 = event.y - CONST.POINT_RADIUS
            x1 = event.x + CONST.POINT_RADIUS
            y1 = event.y + CONST.POINT_RADIUS
            node_id = self.create_oval(x0, y0, x1, y1, fill=CONST.NODE_NON_SELECTED_COLOR, outline='')
            self.nodes[node_id] = []
            return

        if clicked_node[0] not in self.nodes:
            return  # non node clicked

        if clicked_node[0] in self.selected:
            self.itemconfig(clicked_node[0], fill=CONST.NODE_NON_SELECTED_COLOR)
            self.selected.remove(clicked_node[0])
        else:
            self.itemconfig(clicked_node[0], fill=CONST.NODE_SELECTED_COLOR)
            self.selected.append(clicked_node[0])

    def add_double_side_edges(self):
        for i, n1 in enumerate(self.selected):
            for j, n2 in enumerate(self.selected):
                if i == j or (n1, n2) in self.edges:
                    continue

                x1, y1 = self._get_node_center(n1)
                x2, y2 = self._get_node_center(n2)

                edge_id = self.create_line(x1, y1, x2, y2, fill=CONST.EDGE_COLOR, width=.5)
                self.tag_lower(edge_id)
                self.edges[(n1, n2)] = edge_id

                self.nodes[n1].append(n2)

            self.itemconfig(n1, fill=CONST.NODE_NON_SELECTED_COLOR)

        self.selected = []

    def on_drag(self, event):
        clicked_node = self.find_withtag("current")

        if clicked_node[0] not in self.nodes:
            return  # non node clicked

        if clicked_node:
            x1_center, y1_center = self._get_node_center(clicked_node[0])
            dx = event.x - x1_center
            dy = event.y - y1_center

            self.move(clicked_node[0], dx, dy)

            for n1, n2 in self.edges.keys():
                if n1 == clicked_node[0] or n2 == clicked_node[0]:
                    self._update_edge_position(n1, n2)

    def clear_graph(self):
        self.nodes = {}
        self.selected = []
        self.edges = {}
        self.delete("all")

    def add_one_side_edges(self):
        for i, n1 in enumerate(self.selected):
            for j, n2 in enumerate(self.selected):
                if i >= j or (n1, n2) in self.edges:
                    continue

                x1, y1 = self._get_node_center(n1)
                x2, y2 = self._get_node_center(n2)

                edge_id = self.create_line(x1, y1, x2, y2, fill=CONST.EDGE_COLOR, width=CONST.EDGE_WIDTH)
                self.tag_lower(edge_id)
                self.edges[(n1, n2)] = edge_id

                self.nodes[n1].append(n2)

            self.itemconfig(n1, fill=CONST.NODE_NON_SELECTED_COLOR)

        self.selected = []

    def generate_random_graph(self):
        for _ in range(CONST.RANDOM_GRAPH_POINTS):
            while True:
                x = random.randint(math.floor(CONST.POINT_RADIUS),
                                   math.floor(CONST.CANVAS_WIDTH_PX - CONST.POINT_RADIUS))
                y = random.randint(math.floor(CONST.POINT_RADIUS),
                                   math.floor(CONST.CANVAS_HEIGHT_PX - CONST.POINT_RADIUS))
                x0 = x - CONST.POINT_RADIUS
                y0 = y - CONST.POINT_RADIUS
                x1 = x + CONST.POINT_RADIUS
                y1 = y + CONST.POINT_RADIUS

                overlapping = self.find_overlapping(x0, y0, x1, y1)

                if not overlapping:
                    node_id = self.create_oval(x0, y0, x1, y1, fill=CONST.NODE_NON_SELECTED_COLOR, outline='')
                    self.nodes[node_id] = []

                    available_nodes = list(filter(lambda k: k != node_id, self.nodes.keys()))
                    if len(available_nodes) > 0:
                        random_node = random.choice(available_nodes)
                        self.selected = [node_id, random_node]
                        # When a is set to 0 then more nodes might be without edges
                        choice = random.randint(1, 100)
                        if choice == 0:
                            self.selected = []
                        elif choice <= 55:
                            self.add_one_side_edges()
                        else:
                            self.add_double_side_edges()
                    break

    def force_direct_graph_algorithm(self):
        positions = {node_id: (self._get_node_center(node_id)) for node_id in self.nodes.keys()}
        nodes_edges = []

        for n1_id, nodes in self.nodes.items():
            for n2_id in nodes:
                nodes_edges.append((n1_id, n2_id))

        fdg = ForceDirectGraph(
            positions=positions,
            edges=nodes_edges,
            max_iterations=CONST.FDG_ITERATIONS,
            repulsion_const=CONST.FDG_REPULSION_CONSTANT,
            damping_const=CONST.FDG_DAMPING_CONSTANT,
            attraction_constant=CONST.FDG_ATTRACTION_CONSTANT
        )

        for index, positions_dict in enumerate(fdg):
            for node_id, new_coords in positions_dict.items():
                x1_center, y1_center = self._get_node_center(node_id)
                dx = new_coords[0] - x1_center
                dy = new_coords[1] - y1_center

                new_x = x1_center + dx
                new_y = y1_center + dy
                new_x, new_y = self._apply_constraints(new_x, new_y)

                self.move(node_id, new_x - x1_center, new_y - y1_center)

                for n1, n2 in self.edges.keys():
                    if n1 == node_id or n2 == node_id:
                        self._update_edge_position(n1, n2)

            self.update()
            time.sleep(0.1)

    def import_edges(self, text_field):
        self.clear_graph()

        unique_digits = set()

        for edge in text_field.get("1.0", "end").splitlines():
            if len(edge) > 0:
                digits = edge.split()
                unique_digits.update(map(int, digits))

        def generate_random_squares(num):
            square_size = 2 * CONST.POINT_RADIUS
            x_coords = list(range(0, CONST.CANVAS_WIDTH_PX, square_size))
            y_coords = list(range(0, CONST.CANVAS_HEIGHT_PX, square_size))

            all_positions = [(x, y) for x in x_coords for y in y_coords]

            if len(all_positions) < num:
                print('Za mała siatka')
                return

            random.shuffle(all_positions)

            return all_positions[:num]

        positions = generate_random_squares(len(unique_digits))

        node_id_to_tk_id = {}

        for node_id, position in zip(unique_digits, positions):
            x0 = position[0]
            y0 = position[1]
            x1 = x0 + 2 * CONST.POINT_RADIUS
            y1 = y0 + 2 * CONST.POINT_RADIUS
            tk_id = self.create_oval(x0, y0, x1, y1, fill=CONST.NODE_NON_SELECTED_COLOR, outline='')
            self.nodes[tk_id] = []
            node_id_to_tk_id[node_id] = tk_id

        self.update()

        for edge in text_field.get("1.0", "end").splitlines():
            if len(edge) > 0:
                node_1, node_2 = edge.split()
                node_1 = node_id_to_tk_id[int(node_1)]
                node_2 = node_id_to_tk_id[int(node_2)]
                x1, y1 = self._get_node_center(node_1)
                x2, y2 = self._get_node_center(node_2)
                self.nodes[node_1].append(node_2)
                edge_id = self.create_line([x1, y1, x2, y2], fill=CONST.EDGE_COLOR, width=CONST.EDGE_WIDTH)
                self.tag_lower(edge_id)
                self.edges[(node_1, node_2)] = edge_id

        self.update()

        text_field.delete("1.0", tk.END)
        text_field.insert("1.0", "Import finished\n")

    def remove_edges(self):
        self.delete(*self.edges.values())
        self.update()

    def louvain_method(self, btn, text_input):
        btn["state"] = "disabled"
        text_input.delete("1.0", tk.END)
        text_input.insert("1.0", "Louvain started\n")
        text_input.update()
        # Step 1: Initialization - Each community is a single node
        current_partition = {node: node for node in self.nodes}
        current_modularity = self._calculate_modularity(self.nodes, current_partition)
        best_partition = current_partition
        best_modularity = current_modularity
        print(f"Initial modularity: {current_modularity:.4f}")
        text_input.insert(tk.END, f"Initial modularity: {current_modularity:.4f}\n")
        text_input.update()

        while True:
            improved = False

            for node in self.nodes:
                current_community = current_partition[node]

                neighbor_communities = defaultdict(int)
                for neighbor in self.nodes[node]:
                    neighbor_communities[current_partition[neighbor]] += 1

                if len(self.nodes[node]) == 0:
                    for n_id, neighbors in self.nodes.items():
                        if node in neighbors:
                            neighbor_community = best_partition[n_id]
                            neighbor_communities[neighbor_community] += 1

                best_community = max(neighbor_communities, key=neighbor_communities.get, default=None)

                if best_community != current_community and best_community is not None:
                    current_partition[node] = best_community
                    improved = True

            new_modularity = self._calculate_modularity(self.nodes, current_partition)
            print(f"New modularity: {new_modularity:.4f}")
            text_input.insert(tk.END, f"New modularity: {new_modularity:.4f}\n")
            text_input.update()

            if new_modularity > best_modularity:
                best_partition = current_partition
                best_modularity = new_modularity

            if not improved:
                break

        print(f"Best modularity: {best_modularity:.4f}")
        text_input.insert(tk.END, f"Best modularity: {best_modularity:.4f}\n")
        text_input.update()

        if len(set(best_partition.values())) <= 50:
            community_colors = {value: self.colors.pop() for value in set(best_partition.values())}
        else:
            community_colors = {value: self._get_random_hex_color() for value in set(best_partition.values())}

        if len(self.nodes) < 100:
            for node_id in self.nodes:
                self.itemconfig(node_id, fill=community_colors[best_partition[node_id]])
                self.resize_node(node_id, 8)

            return

        # Step 2: Creating a new graph (community aggregation)
        communities = defaultdict(list)

        for node, community in best_partition.items():
            communities[community].append(node)

        new_nodes = {}
        for community, members in communities.items():
            self.itemconfig(community, fill=community_colors[community])
            new_neighbors = set()
            for member in members:
                for neighbor in self.nodes[member]:
                    if neighbor not in members:
                        new_neighbors.add(best_partition[neighbor])

            new_nodes[community] = list(new_neighbors)

        for edge_id in self.edges.values():
            self.delete(edge_id)

        self.edges = {}
        self.update()

        for node in self.nodes.keys():
            if node in new_nodes.keys():
                if len(new_nodes[node]) == 0 and node not in list(chain(*new_nodes.values())):
                    self.delete(node)
                    del new_nodes[node]
                    continue

                for neighbor in new_nodes[node]:
                    x1, y1 = self._get_node_center(node)
                    x2, y2 = self._get_node_center(neighbor)
                    edge_id = self.create_line([x1, y1, x2, y2], fill=CONST.EDGE_COLOR, width=CONST.EDGE_WIDTH)
                    self.tag_lower(edge_id)
                    self.edges[(node, neighbor)] = edge_id
            else:
                self.delete(node)

        self.update()
        self.nodes = new_nodes

        for node in self.nodes:
            self.resize_node(node, 8)

        btn["state"] = "normal"
        self.update()
        print('Louvain done')
        text_input.insert(tk.END, 'Louvain done')

    def resize_node(self, node_id, r):
        x1, y1, x2, y2 = self.coords(node_id)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        current_radius = (x2 - x1) / 2
        new_radius = current_radius + r
        self.coords(node_id, cx - new_radius, cy - new_radius, cx + new_radius, cy + new_radius)

    def _calculate_modularity(self, nodes, partition):
        m = sum(len(neighbors) for neighbors in nodes.values()) // 2  # Liczba krawędzi w grafie
        modularity = 0.0

        for community in set(partition.values()):
            community_nodes = [node for node, com in partition.items() if com == community]

            # Liczba krawędzi wewnątrz społeczności
            lc = 0
            for node in community_nodes:
                for neighbor in nodes[node]:
                    if neighbor in community_nodes:
                        lc += 1
            lc //= 2  # Każda krawędź jest liczona dwukrotnie

            # Suma stopni w społeczności
            dc = sum(len(nodes[node]) for node in community_nodes)

            modularity += lc / m - (dc / (2 * m)) ** 2
        return modularity

    def _draw_edges(self):
        self.delete(self.edge)

    def _update_edge_position(self, n1, n2):
        edge = self.edges[(n1, n2)]
        x1, y1 = self._get_node_center(n1)
        x2, y2 = self._get_node_center(n2)
        self.coords(edge, x1, y1, x2, y2)

        self.nodes[n1] = [id_ if id_ == n2 else id_ for id_ in self.nodes[n1]]

    def _get_node_center(self, node_id):
        coords = self.coords(node_id)
        x_center = (coords[0] + coords[2]) / 2
        y_center = (coords[1] + coords[3]) / 2
        return x_center, y_center

    def _calc_node_distances(self, n1, n2):
        x1, y1 = self._get_node_center(n1)
        x2, y2 = self._get_node_center(n2)

        return int(math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2))

    def _apply_constraints(self, x, y):
        x = max(
            0 + (2 * CONST.POINT_RADIUS),
            min(CONST.CANVAS_WIDTH_PX - (2 * CONST.POINT_RADIUS), x)
        )
        y = max(
            0 + (2 * CONST.POINT_RADIUS),
            min(CONST.CANVAS_HEIGHT_PX - (2 * CONST.POINT_RADIUS), y)
        )
        return x, y

    def _get_random_hex_color(self) -> str:
        color = None

        while color is None:
            temp = f'#{random.randint(0, 0xFFFFFF):06x}'
            if temp not in self.colors:
                color = temp
                self.colors.append(color)

        return color
