import tkinter as tk
from graph import Graph, CONST


def build_tk():
    root = tk.Tk()
    root.title("Graph project")
    root.geometry(f"{CONST.APP_WIDTH_PX}x{CONST.APP_HEIGHT_PX}")
    root.resizable(width=False, height=False)

    main_column = tk.Frame(root)
    main_column.pack(fill=tk.BOTH, expand=False)

    row_1 = tk.Frame(main_column)
    row_1.pack(side=tk.TOP, fill=tk.BOTH)

    canvas = Graph(row_1, width=CONST.CANVAS_WIDTH_PX, height=CONST.CANVAS_HEIGHT_PX, bg="#8f8f8f")
    canvas.pack(side=tk.LEFT)

    text_input = tk.Text(row_1)
    text_input.pack(side=tk.LEFT, fill=tk.BOTH)

    row2 = tk.Frame(main_column)
    row2.pack(side=tk.TOP)

    one_side_edges_btn = tk.Button(row2, text="One-sided edges", command=canvas.add_one_side_edges)
    one_side_edges_btn.pack(side=tk.LEFT)

    double_side_edges_btn = tk.Button(row2, text="Double-sided edges", command=canvas.add_double_side_edges)
    double_side_edges_btn.pack(side=tk.LEFT)

    random_graph_btn = tk.Button(row2, text="Random graph", command=canvas.generate_random_graph)
    random_graph_btn.pack(side=tk.LEFT)

    louvain_btn = tk.Button(
        row2,
        text="Louvain method",
        command=lambda: canvas.louvain_method(louvain_btn, text_input)
    )
    louvain_btn.pack(side=tk.LEFT)

    louvain_btn = tk.Button(
        row2,
        text="Remove edges",
        command=canvas.remove_edges
    )
    louvain_btn.pack(side=tk.LEFT)

    force_direct_graph_btn = tk.Button(row2, text="Force-direct graph", command=canvas.force_direct_graph_algorithm)
    force_direct_graph_btn.pack(side=tk.LEFT)

    force_direct_graph_btn = tk.Button(row2, text="Import edges", command=lambda: canvas.import_edges(text_input))
    force_direct_graph_btn.pack(side=tk.LEFT)

    reset_btn = tk.Button(row2, text="Reset", command=canvas.clear_graph)
    reset_btn.pack(side=tk.LEFT)

    quit_btn = tk.Button(row2, text="Close", command=root.quit)
    quit_btn.pack(side=tk.RIGHT)

    canvas.bind("<Button-1>", canvas.on_click)
    canvas.bind("<B1-Motion>", canvas.on_drag)

    return root


app = build_tk()
app.mainloop()
