import tkinter as tk
import math
import random
from algorithm import ForceDirectGraph
import time


class CONST:
    APP_WIDTH_PX = 1000
    APP_HEIGHT_PX = 640
    CANVAS_WIDTH_PX = APP_WIDTH_PX - 200
    CANVAS_HEIGHT_PX = APP_HEIGHT_PX - 40

    RANDOM_GRAPH_POINTS = 50
    POINT_RADIUS = 1
    EDGE_WIDTH = .5

    FDG_ITERATIONS = 300
    FDG_REPULSION_CONSTANT = 5000
    FDG_ATTRACTION_CONSTANT = 0.2
    FDG_DAMPING_CONSTANT = 0.3

    NODE_NON_SELECTED_COLOR = 'blue'
    NODE_SELECTED_COLOR = 'yellow'
    EDGE_COLOR = 'white'


class Graph(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.nodes = {}  # node_from: [node_to] -> node_from: [(node_to, weight)]
        self.selected = []  # list of node_id
        self.edges = {}  # (node_from, node_to): edge_id
        self.texts = {}  # edge_id: text_id

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

                edge_id = self.create_line(x1, y1, x2, y2, fill=CONST.EDGE_COLOR, width=.5, arrow=tk.LAST)
                self.tag_lower(edge_id)
                self.edges[(n1, n2)] = edge_id

                weight = self._calc_node_distances(n1, n2)
                self._add_text_on_line(edge_id, weight)

                self.nodes[n1].append((n2, weight))

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
        self.texts = {}
        self.delete("all")

    def add_one_side_edges(self, hide_text=False, arrow=True):
        for i, n1 in enumerate(self.selected):
            for j, n2 in enumerate(self.selected):
                if i >= j or (n1, n2) in self.edges:
                    continue

                x1, y1 = self._get_node_center(n1)
                x2, y2 = self._get_node_center(n2)

                edge_id = self.create_line(x1, y1, x2, y2, fill=CONST.EDGE_COLOR, width=CONST.EDGE_WIDTH, arrow=tk.LAST if arrow else None)
                self.tag_lower(edge_id)
                self.edges[(n1, n2)] = edge_id

                weight = self._calc_node_distances(n1, n2)
                if not hide_text:
                    self._add_text_on_line(edge_id, weight)

                self.nodes[n1].append((n2, weight))

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
            for n2_id, _ in nodes:
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

        lines = []
        for edge in text_field.get("1.0", "end").splitlines():
            if len(edge) > 0:
                node_1, node_2 = edge.split()
                x1, y1 = self._get_node_center(node_id_to_tk_id[int(node_1)])
                x2, y2 = self._get_node_center(node_id_to_tk_id[int(node_2)])
                lines.extend([x1, y1, x2, y2])

        z = self.create_line(lines, fill=CONST.EDGE_COLOR, width=CONST.EDGE_WIDTH)

        '''
        def put_node(nodes: list):
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

                if not overlapping or not any(o in nodes for o in overlapping):
                    node_id = self.create_oval(x0, y0, x1, y1, fill=CONST.NODE_NON_SELECTED_COLOR, outline='')
                    self.nodes[node_id] = []
                    return node_id

        node_id_to_tk_id = {}  # node_id: tkinker_id
        for edge in text_field.get("1.0", "end").splitlines():
            if len(edge) > 0:
                node_1, node_2 = edge.split()
                # print(f"{node_1} -> {node_2}")
                if node_1 not in node_id_to_tk_id:
                    tk_id = put_node(list(node_id_to_tk_id.values()))
                    node_id_to_tk_id[node_1] = tk_id

                if node_2 not in node_id_to_tk_id:
                    tk_id = put_node(list(node_id_to_tk_id.values()))
                    node_id_to_tk_id[node_2] = tk_id

                # self.selected.append(node_id_to_tk_id[node_1])
                # self.selected.append(node_id_to_tk_id[node_2])
                # self.add_one_side_edges(hide_text=True)
            self.update()

        text_field.delete("1.0", tk.END)
        text_field.insert("1.0", "Import done")
        '''

    def _update_edge_position(self, n1, n2):
        edge = self.edges[(n1, n2)]
        x1, y1 = self._get_node_center(n1)
        x2, y2 = self._get_node_center(n2)
        self.coords(edge, x1, y1, x2, y2)

        new_weight = self._calc_node_distances(n1, n2)
        # self._update_text(edge, text=new_weight)
        self.nodes[n1] = [(id_, new_weight) if id_ == n2 else (id_, weight) for (id_, weight) in self.nodes[n1]]

    def _get_node_center(self, node_id):
        coords = self.coords(node_id)
        x_center = (coords[0] + coords[2]) / 2
        y_center = (coords[1] + coords[3]) / 2
        return x_center, y_center

    def _add_text_on_line(self, edge, text):
        coords = self.coords(edge)
        x_center = (coords[0] + coords[2]) / 2
        y_center = (coords[1] + coords[3]) / 2

        text_id = self.create_text(x_center, y_center, text=text, fill="black", font=("Arial", 10, "bold"))

        self.texts[edge] = text_id

    def _update_text(self, edge, text):
        edge_coords = self.coords(edge)
        x_center = (edge_coords[0] + edge_coords[2]) / 2
        y_center = (edge_coords[1] + edge_coords[3]) / 2

        text_id = self.texts[edge]

        self.coords(text_id, x_center, y_center)
        self.itemconfig(text_id, text=f"{text}")

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
