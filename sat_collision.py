import tkinter as tk
import math

def make_rect_vertices(cx, cy, w, h, angle_deg):
    "Retorna los 4 vértices de un OBB centrado en (cx,cy) con rotación."
    a = math.radians(angle_deg)
    cos_a, sin_a = math.cos(a), math.sin(a)
    hw, hh = w / 2, h / 2
    corners = [(-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh)]
    return [(cx + x * cos_a - y * sin_a, cy + x * sin_a + y * cos_a)
            for x, y in corners]


def get_axes(vertices):
    "Obtiene los ejes separadores (normales de cada arista) del polígono."
    axes = []
    n = len(vertices)
    for i in range(n):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % n]
        edge_x, edge_y = x2 - x1, y2 - y1
        # Normal perpendicular a la arista 
        length = math.hypot(edge_x, edge_y)
        if length > 0:
            axes.append((-edge_y / length, edge_x / length))
    return axes


def project(vertices, axis):
    "Proyecta todos los vértices sobre el eje y retorna (min, max)."
    ax, ay = axis
    dots = [vx * ax + vy * ay for vx, vy in vertices]
    return min(dots), max(dots)


def overlaps(min_a, max_a, min_b, max_b):
    "¿Hay solapamiento entre dos intervalos?"
    return max_a >= min_b and max_b >= min_a


def sat_collision(verts_a, verts_b):
    
    axes = get_axes(verts_a) + get_axes(verts_b)
    min_overlap = float('inf')
    mtv_axis = None

    for axis in axes:
        min_a, max_a = project(verts_a, axis)
        min_b, max_b = project(verts_b, axis)

        if not overlaps(min_a, max_a, min_b, max_b):
            # Eje separador encontrado, NO hay colisión
            return False, None, 0

        overlap = min(max_a, max_b) - max(min_a, min_b)
        if overlap < min_overlap:
            min_overlap = overlap
            mtv_axis = axis

    # Si llegamos aquí, todos los ejes se solapan, HAY colisión
    return True, mtv_axis, min_overlap

class SATDemo:
    # Rectángulo estático 
    RECT_A = dict(cx=400, cy=300, w=160, h=80, angle=0)
    # Rectángulo móvil 
    RECT_B_INIT = dict(cx=620, cy=200, w=200, h=90, angle=30)

    COLORS = {
        "bg": "#FAFAF5",
        "canvas_bg": "#F7F6E8",
        "rect_a": "#E05252",
        "rect_b": "#4A90D9",
        "rect_a_fill": "#FDDEDE",
        "rect_b_fill": "#D6EAFB",
        "collision_fill": "#FFD700",
        "axis": "#888888",
        "proj_a": "#E05252",
        "proj_b": "#4A90D9",
        "overlap": "#FF8C00",
        "text_ok": "#2E8B57",
        "text_col": "#CC0000",
        "panel": "#EEEEE0",
        "border": "#CCCCAA",
    }

    def __init__(self, root):
        self.root = root
        root.title("SAT — Separating Axis Theorem  |  Detección de Colisiones")
        root.configure(bg=self.COLORS["bg"])
        root.resizable(True, True)

        # Estado del rectángulo B
        self.bx = self.RECT_B_INIT["cx"]
        self.by = self.RECT_B_INIT["cy"]
        self.bw = self.RECT_B_INIT["w"]
        self.bh = self.RECT_B_INIT["h"]
        self.b_angle = self.RECT_B_INIT["angle"]

        self._drag_start = None
        
        self._build_ui()
        self._redraw()

    # Iterfaz

    def _build_ui(self):
        # Título
        title = tk.Label(self.root, text="Separating Axis Theorem (SAT)",
                         font=("Helvetica", 16, "bold"),
                         bg=self.COLORS["bg"], fg="#333333")
        title.pack(pady=(10, 0))

        subtitle = tk.Label(self.root,
            font=("Helvetica", 10), bg=self.COLORS["bg"], fg="#666666")
        subtitle.pack(pady=(0, 6))

        # Frame principal
        main = tk.Frame(self.root, bg=self.COLORS["bg"])
        main.pack(fill=tk.BOTH, expand=True, padx=10, pady=4)

        # Canvas
        self.canvas = tk.Canvas(main, width=800, height=520,
                                bg=self.COLORS["canvas_bg"],
                                highlightbackground=self.COLORS["border"],
                                highlightthickness=2, cursor="crosshair")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind("<ButtonPress-1>",   self._on_press)
        self.canvas.bind("<B1-Motion>",       self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)

        # Panel derecho
        panel = tk.Frame(main, bg=self.COLORS["panel"],
                         bd=1, relief=tk.SUNKEN, width=220)
        panel.pack(side=tk.RIGHT, fill=tk.Y, padx=(8, 0))
        panel.pack_propagate(False)
        self._build_panel(panel)

    def _build_panel(self, panel):
        def section(text):
            tk.Label(panel, text=text, font=("Helvetica", 10, "bold"),
                     bg=self.COLORS["panel"], fg="#444444",
                     anchor="w").pack(fill=tk.X, padx=8, pady=(12, 2))

        def separator():
            tk.Frame(panel, height=1, bg=self.COLORS["border"]).pack(
                fill=tk.X, padx=8, pady=2)

        # Estado de colisión
        self.status_var = tk.StringVar(value="SIN COLISIÓN")
        self.status_lbl = tk.Label(panel, textvariable=self.status_var,
                                   font=("Helvetica", 15, "bold"),
                                   bg=self.COLORS["text_ok"], fg="white",
                                   pady=10, relief=tk.RAISED)
        self.status_lbl.pack(fill=tk.X, padx=8, pady=(14, 4))

        # Información SAT
        section("Información SAT")
        separator()
        self.info_var = tk.StringVar(value="")
        tk.Label(panel, textvariable=self.info_var, font=("Courier", 9),
                 bg=self.COLORS["panel"], fg="#333333",
                 justify=tk.LEFT, anchor="w", wraplength=200).pack(
            fill=tk.X, padx=10, pady=4)

        # Rectángulo B — controles
        section("Rectángulo Azul (arrastrable)")
        separator()

        self._slider("Rotación (°)", -180, 180, self.b_angle,
                     self._on_angle, panel)
        self._slider("Ancho", 40, 350, self.bw, self._on_width,  panel)
        self._slider("Alto",  30, 250, self.bh, self._on_height, panel)

        # Rectángulo A — controles
        section("Rectángulo Rojo (fijo)")
        separator()

        self.a_angle_var = tk.DoubleVar(value=self.RECT_A["angle"])
        self._slider("Rotación (°)", -180, 180, self.RECT_A["angle"],
                     self._on_a_angle, panel, var=self.a_angle_var)

        # Botones
        separator()
        tk.Button(panel, text="Resetear posición",
                  command=self._reset,
                  bg="#E8E8D0", relief=tk.FLAT,
                  font=("Helvetica", 9)).pack(fill=tk.X, padx=8, pady=(8, 4))

    def _slider(self, label, from_, to, init, cmd, parent, var=None):
        tk.Label(parent, text=label, font=("Helvetica", 9),
                 bg=self.COLORS["panel"], fg="#555555",
                 anchor="w").pack(fill=tk.X, padx=10, pady=(6, 0))
        if var is None:
            var = tk.DoubleVar(value=init)
        s = tk.Scale(parent, variable=var, from_=from_, to=to,
                     orient=tk.HORIZONTAL, resolution=1,
                     command=cmd, bg=self.COLORS["panel"],
                     troughcolor="#CCCCAA", highlightthickness=0,
                     sliderrelief=tk.FLAT, length=190)
        s.pack(padx=10)
        return s, var

    # Callbacks de controles

    def _on_angle(self, val):
        self.b_angle = float(val); self._redraw()

    def _on_width(self, val):
        self.bw = float(val); self._redraw()

    def _on_height(self, val):
        self.bh = float(val); self._redraw()

    def _on_a_angle(self, val):
        self.RECT_A["angle"] = float(val); self._redraw()

    def _reset(self):
        self.bx = self.RECT_B_INIT["cx"]
        self.by = self.RECT_B_INIT["cy"]
        self.bw = self.RECT_B_INIT["w"]
        self.bh = self.RECT_B_INIT["h"]
        self.b_angle = self.RECT_B_INIT["angle"]
        self.RECT_A["angle"] = 0
        self._redraw()

    # Drag 

    def _on_press(self, event):
        verts = make_rect_vertices(self.bx, self.by, self.bw, self.bh, self.b_angle)
        if self._point_in_polygon(event.x, event.y, verts):
            self._drag_start = (event.x - self.bx, event.y - self.by)

    def _on_drag(self, event):
        if self._drag_start:
            dx, dy = self._drag_start
            self.bx = event.x - dx
            self.by = event.y - dy
            self._redraw()

    def _on_release(self, event):
        self._drag_start = None

    def _point_in_polygon(self, px, py, verts):
        "Ray casting para detectar si el punto está dentro del polígono."
        n = len(verts)
        inside = False
        j = n - 1
        for i in range(n):
            xi, yi = verts[i]
            xj, yj = verts[j]
            if ((yi > py) != (yj > py)) and (px < (xj - xi) * (py - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside

    # Dibujo 

    def _redraw(self):
        c = self.canvas
        c.delete("all")

        a = self.RECT_A
        verts_a = make_rect_vertices(a["cx"], a["cy"], a["w"], a["h"], a["angle"])
        verts_b = make_rect_vertices(self.bx, self.by, self.bw, self.bh, self.b_angle)

        collision, mtv_axis, mtv_depth = sat_collision(verts_a, verts_b)

        # Fondo grid 
        for x in range(0, 801, 40):
            c.create_line(x, 0, x, 520, fill="#EEEED8", width=1)
        for y in range(0, 521, 40):
            c.create_line(0, y, 800, y, fill="#EEEED8", width=1)

        self._draw_axes(verts_a, verts_b)

        if collision:
            self._draw_projections(verts_a, verts_b)

        if collision and mtv_axis:
            self._draw_mtv(mtv_axis, mtv_depth)
            
        # Polígonos 
        fill_a = self.COLORS["collision_fill"] if collision else self.COLORS["rect_a_fill"]
        fill_b = self.COLORS["collision_fill"] if collision else self.COLORS["rect_b_fill"]

        c.create_polygon(*[coord for v in verts_a for coord in v],
                         fill=fill_a, outline=self.COLORS["rect_a"], width=3)
        c.create_polygon(*[coord for v in verts_b for coord in v],
                         fill=fill_b, outline=self.COLORS["rect_b"], width=3)

        # Centros
        ax, ay = a["cx"], a["cy"]
        c.create_oval(ax-5, ay-5, ax+5, ay+5, fill=self.COLORS["rect_a"], outline="")
        c.create_oval(self.bx-5, self.by-5, self.bx+5, self.by+5,
                      fill=self.COLORS["rect_b"], outline="")

        # Etiquetas de rectángulos
        c.create_text(ax, ay - 55, text="A", font=("Helvetica", 13, "bold"),
                      fill=self.COLORS["rect_a"])
        c.create_text(self.bx, self.by - 60, text="B",
                      font=("Helvetica", 13, "bold"),
                      fill=self.COLORS["rect_b"])

        # ── Panel de estado ──
        self._update_status(collision, mtv_axis, mtv_depth, verts_a, verts_b)


    def _draw_axes(self, verts_a, verts_b):
        "Dibuja los ejes candidatos del SAT."
        c = self.canvas
        cx, cy = 400, 260  # centro de visualización de ejes
        length = 60
        axes = get_axes(verts_a) + get_axes(verts_b)
        seen = set()
        for ax, ay in axes:
            # Evitar duplicados (eje y su opuesto)
            key = (round(abs(ax), 3), round(abs(ay), 3))
            if key in seen:
                continue
            seen.add(key)

            x1, y1 = cx - ax * length, cy - ay * length
            x2, y2 = cx + ax * length, cy + ay * length
            c.create_line(x1, y1, x2, y2,
                          fill=self.COLORS["axis"], width=1,
                          dash=(4, 3), arrow=tk.LAST, arrowshape=(8, 10, 4))

        c.create_text(cx, cy - length - 10, text="Ejes SAT",
                      font=("Helvetica", 8), fill="#999999")

    def _draw_projections(self, verts_a, verts_b):
        "Dibuja las proyecciones del eje con menor overlap (eje MTV)."
        c = self.canvas
        axes = get_axes(verts_a) + get_axes(verts_b)
        min_overlap = float('inf')
        best_axis = None
        for axis in axes:
            min_a, max_a = project(verts_a, axis)
            min_b, max_b = project(verts_b, axis)
            if overlaps(min_a, max_a, min_b, max_b):
                ov = min(max_a, max_b) - max(min_a, min_b)
                if ov < min_overlap:
                    min_overlap = ov
                    best_axis = axis

        if best_axis is None:
            return

        ax, ay = best_axis
        perp = (-ay, ax)  # perpendicular al eje (para desplazar la línea)
        y_base = 490
        scale = 2.5

        min_a, max_a = project(verts_a, best_axis)
        min_b, max_b = project(verts_b, best_axis)

        # Línea base
        c.create_line(20, y_base, 780, y_base, fill="#CCCCBB", width=1)
        c.create_text(400, y_base - 12, text=f"Proyección eje MTV  (overlap={min_overlap:.1f}px)",
                      font=("Helvetica", 8, "italic"), fill="#888888")

        offset = 400
        def to_screen(val):
            return offset + val * scale

        # Proyección A
        xa1, xa2 = to_screen(min_a), to_screen(max_a)
        c.create_line(xa1, y_base - 6, xa2, y_base - 6,
                      fill=self.COLORS["rect_a"], width=5, capstyle=tk.ROUND)
        # Proyección B
        xb1, xb2 = to_screen(min_b), to_screen(max_b)
        c.create_line(xb1, y_base + 6, xb2, y_base + 6,
                      fill=self.COLORS["rect_b"], width=5, capstyle=tk.ROUND)
        # Overlap
        ov_left  = max(xa1, xb1)
        ov_right = min(xa2, xb2)
        if ov_right > ov_left:
            c.create_line(ov_left, y_base, ov_right, y_base,
                          fill=self.COLORS["overlap"], width=9, capstyle=tk.ROUND)

    def _draw_mtv(self, mtv_axis, mtv_depth):
        c = self.canvas
        ax, ay = mtv_axis
        scale = min(mtv_depth * 1.5, 80)
        ex, ey = self.bx + ax * scale, self.by + ay * scale

        c.create_line(self.bx, self.by, ex, ey,
                      fill=self.COLORS["overlap"], width=3,
                      arrow=tk.LAST, arrowshape=(12, 14, 5))
        c.create_text(ex + 8, ey, text=f"MTV\n{mtv_depth:.1f}px",
                      font=("Helvetica", 8, "bold"),
                      fill=self.COLORS["overlap"], anchor="w")

    def _update_status(self, collision, mtv_axis, mtv_depth, verts_a, verts_b):
        if collision:
            self.status_var.set("COLISIÓN")
            self.status_lbl.config(bg=self.COLORS["text_col"])
        else:
            self.status_var.set("SIN COLISIÓN")
            self.status_lbl.config(bg=self.COLORS["text_ok"])

        axes_a = get_axes(verts_a)
        axes_b = get_axes(verts_b)
        total_axes = len(set(
            (round(abs(ax), 2), round(abs(ay), 2))
            for ax, ay in axes_a + axes_b
        ))

        info = (
            f"Rect A  ({self.RECT_A['w']}×{self.RECT_A['h']})\n"
            f"  ángulo: {self.RECT_A['angle']:.0f}°\n"
            f"  centro: ({self.RECT_A['cx']}, {self.RECT_A['cy']})\n\n"
            f"Rect B  ({self.bw:.0f}×{self.bh:.0f})\n"
            f"  ángulo: {self.b_angle:.0f}°\n"
            f"  centro: ({self.bx:.0f}, {self.by:.0f})\n\n"
            f"Ejes evaluados: {len(axes_a)+len(axes_b)}\n"
            f"(únicos: {total_axes})\n"
        )
        if collision and mtv_axis:
            info += f"\nMTV profundidad: {mtv_depth:.2f}px"
            info += f"\nMTV eje: ({mtv_axis[0]:.2f}, {mtv_axis[1]:.2f})"
        else:
            info += "\nEje separador: ENCONTRADO" if not collision else ""

        self.info_var.set(info)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1060x600")
    app = SATDemo(root)
    root.mainloop()
