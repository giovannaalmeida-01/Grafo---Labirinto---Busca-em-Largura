import tkinter as tk
from collections import deque

class MazeSolverGUI:
    GRID_WIDTH = 30
    GRID_HEIGHT = 20
    CELL_SIZE = 25
    ANIMATION_DELAY_MS = 50

    COLORS = {
        '#': "#1E3A5F",  # Parede (Azul Escuro)
        ' ': "#FFFFFF",  # Caminho (Branco)
        'S': "#4CAF50",  # Início (Verde)
        'E': "#F44336",  # Fim (Vermelho)
        'F': "#AED6F1",  # Fronteira/Fila (Azul Claro)
        'V': "#D6EAF8",  # Visitado (Azul Pálido)
        'P': "#FFD700",  # Caminho Final (Dourado)
    }
    
    TOOL_MAP = {
        "Parede (#)": '#',
        "Caminho ( )": ' ',
        "Início (S)": 'S',
        "Fim (E)": 'E',
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Solucionador de Labirintos Interativo (BFS)")

        self.labirimento = [[' ' for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]
        self.inicio_pos = None
        self.fim_pos = None
        
        self.grid_cells = [[None for _ in range(self.GRID_WIDTH)] for _ in range(self.GRID_HEIGHT)]

        self.fila = deque()
        self.visitados = set()
        self.predecessores = {}
        self.job_after = None
        self.is_simulating = False

        self._setup_ui()
        self._draw_initial_grid()

    def _setup_ui(self):

        main_frame = tk.Frame(self.root)
        main_frame.pack(padx=10, pady=10)

        canvas_width = self.GRID_WIDTH * self.CELL_SIZE
        canvas_height = self.GRID_HEIGHT * self.CELL_SIZE
        self.canvas = tk.Canvas(main_frame, width=canvas_width, height=canvas_height, bg="white", borderwidth=1, relief="solid")
        self.canvas.pack(side=tk.LEFT, padx=10)

        control_frame = tk.Frame(main_frame)
        control_frame.pack(side=tk.RIGHT, padx=10, anchor="n")

        tk.Label(control_frame, text="Modo Edição:", font=("Arial", 10, "bold")).pack(anchor="w", pady=(0, 5))
        self.tool_var = tk.StringVar(value="Parede (#)")
        
        for text in self.TOOL_MAP.keys():
            rb = tk.Radiobutton(control_frame, text=text, variable=self.tool_var, value=text)
            rb.pack(anchor="w")

        tk.Frame(control_frame, height=2, bd=1, relief=tk.SUNKEN).pack(fill="x", pady=10)

        self.start_button = tk.Button(control_frame, text="Iniciar Busca (BFS)", command=self.iniciar_busca)
        self.start_button.pack(fill="x", pady=5)
        self.reset_button = tk.Button(control_frame, text="Resetar Busca", command=self.resetar_busca, state=tk.DISABLED)
        self.reset_button.pack(fill="x", pady=5)
        self.clear_button = tk.Button(control_frame, text="Limpar Labirinto", command=self.limpar_labirinto)
        self.clear_button.pack(fill="x", pady=5)

        self.canvas.bind("<Button-1>", self._on_canvas_click)
        self.canvas.bind("<B1-Motion>", self._on_canvas_click)
        
    def _draw_initial_grid(self):
        """Desenha a grade inicial no Canvas e preenche self.grid_cells."""
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                x1 = x * self.CELL_SIZE
                y1 = y * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE
                
                rect_id = self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                       fill=self.COLORS[' '], 
                                                       outline="#CCCCCC")
                self.grid_cells[y][x] = rect_id
                
    def _get_cell_coords(self, event):
        """Converte coordenadas de pixel do evento para coordenadas de célula (x, y)."""
        x = event.x // self.CELL_SIZE
        y = event.y // self.CELL_SIZE
        
        if 0 <= x < self.GRID_WIDTH and 0 <= y < self.GRID_HEIGHT:
            return x, y
        return None, None

    def _on_canvas_click(self, event):
        """Manipulador de eventos de clique/arrasto no Canvas."""
        if self.is_simulating:
            return
            
        x, y = self._get_cell_coords(event)
        if x is not None:
            self._edit_cell(x, y)

    def _edit_cell(self, x, y):
        """Atualiza o modelo de dados e a visualização de uma célula."""
        current_tool_text = self.tool_var.get()
        new_char = self.TOOL_MAP[current_tool_text]
        
        if self.labirimento[y][x] == new_char:
            return

        if new_char in ('S', 'E'):
            old_pos = self.inicio_pos if new_char == 'S' else self.fim_pos
            if old_pos:
                ox, oy = old_pos
                self.labirimento[oy][ox] = ' '
                self._update_cell_color(ox, oy, ' ')
            
            if new_char == 'S':
                self.inicio_pos = (x, y)
            else:
                self.fim_pos = (x, y)

        current_char = self.labirimento[y][x]
        if current_char == 'S' and new_char != 'S':
            self.inicio_pos = None
        elif current_char == 'E' and new_char != 'E':
            self.fim_pos = None

        self.labirimento[y][x] = new_char
        self._update_cell_color(x, y, new_char)

    def _update_cell_color(self, x, y, char):
        """Atualiza a cor da célula no Canvas com base no caractere do modelo."""
        color_key = char if char in self.COLORS else ' '
        color = self.COLORS[color_key]
        rect_id = self.grid_cells[y][x]
        self.canvas.itemconfig(rect_id, fill=color)

    def iniciar_busca(self):
        """Inicia o algoritmo BFS."""
        if self.is_simulating:
            return

        if not self.inicio_pos or not self.fim_pos:
            tk.messagebox.showerror("Erro", "Defina os pontos de Início (S) e Fim (E) antes de iniciar a busca.")
            return

        self.is_simulating = True
        self.start_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
        self.reset_button.config(state=tk.NORMAL)
        for child in self.start_button.master.winfo_children():
            if isinstance(child, tk.Radiobutton):
                child.config(state=tk.DISABLED)

        self.resetar_busca(keep_ui=True)

        self.fila = deque([self.inicio_pos])
        self.visitados = {self.inicio_pos}
        self.predecessores = {}
        
        self.processar_passo_bfs()

    def processar_passo_bfs(self):
        """Executa um passo do BFS e agenda o próximo."""
        if not self.fila:
            self.is_simulating = False
            self.start_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
            tk.messagebox.showinfo("Resultado", "Caminho não encontrado.")
            return

        cx, cy = self.fila.popleft()
        
        if (cx, cy) != self.inicio_pos and (cx, cy) != self.fim_pos:
            self._update_cell_color(cx, cy, 'V')

        if (cx, cy) == self.fim_pos:
            self.is_simulating = False
            self.start_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
            self.reconstruir_caminho()
            return

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            nx, ny = cx + dx, cy + dy
            n_pos = (nx, ny)

            if not (0 <= nx < self.GRID_WIDTH and 0 <= ny < self.GRID_HEIGHT):
                continue
            
            if self.labirimento[ny][nx] == '#':
                continue

            if n_pos not in self.visitados:
                self.visitados.add(n_pos)
                self.predecessores[n_pos] = (cx, cy)
                self.fila.append(n_pos)
                
                if n_pos != self.fim_pos:
                    self._update_cell_color(nx, ny, 'F')
        
        self.job_after = self.root.after(self.ANIMATION_DELAY_MS, self.processar_passo_bfs)

    def reconstruir_caminho(self):
        """Traça e pinta o caminho mais curto encontrado."""
        path = []
        current = self.fim_pos
        
        while current and current != self.inicio_pos:
            path.append(current)
            current = self.predecessores.get(current)
        
        if current == self.inicio_pos:
            path.append(self.inicio_pos)
            path.reverse()
            
            for x, y in path:
                if (x, y) != self.inicio_pos and (x, y) != self.fim_pos:
                    self._update_cell_color(x, y, 'P')
            
            tk.messagebox.showinfo("Resultado", f"Caminho encontrado! Comprimento: {len(path) - 1} passos.")
        else:
            tk.messagebox.showinfo("Resultado", "Caminho não encontrado (erro de reconstrução).")

    def resetar_busca(self, keep_ui=False):
        """Limpa os resultados da busca (cores) e reabilita a edição."""
        
        if self.job_after:
            self.root.after_cancel(self.job_after)
            self.job_after = None

        self.fila.clear()
        self.visitados.clear()
        self.predecessores.clear()
        self.is_simulating = False

        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                char = self.labirimento[y][x]
                if char not in ('#', 'S', 'E'):
                    self._update_cell_color(x, y, ' ')
                elif char in ('S', 'E'):
                    self._update_cell_color(x, y, char)

        if not keep_ui:
            self.start_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)
            self.reset_button.config(state=tk.DISABLED)
            for child in self.start_button.master.winfo_children():
                if isinstance(child, tk.Radiobutton):
                    child.config(state=tk.NORMAL)

    def limpar_labirinto(self):
        """Limpa toda a grade para o estado inicial de 'Caminho'."""
        self.resetar_busca() 
        
        for y in range(self.GRID_HEIGHT):
            for x in range(self.GRID_WIDTH):
                self.labirimento[y][x] = ' '
                self._update_cell_color(x, y, ' ')
        
        self.inicio_pos = None
        self.fim_pos = None

if __name__ == "__main__":
    root = tk.Tk()
    app = MazeSolverGUI(root)
    root.mainloop()
    pass
