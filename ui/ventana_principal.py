import tkinter as tk
from tkinter import ttk, messagebox

from models.gesiton_sql import (
    registrar_cliente, registrar_tecnico, registrar_equipo,
    listar_clientes, listar_tecnicos, listar_equipos
)
from models.gestion_poliglota import (
    crear_ticket_completo, cerrar_ticket, consultar_expediente_ticket,
    listar_todos_tickets, agregar_avance_bitacora
)


class VentanaPrincipal:
    # Configuraamos la ventana raíz, estilos y el contenedor de vistas
    def __init__(self, root):
        self.root = root
        self.root.title("Centro de Soporte TI — Gestión de Servicio Técnico")
        self.root.geometry("1080x720")
        self.root.configure(bg="#F4F6F9")

        self.configurar_estilos()

        # Barra superior fija
        header = tk.Frame(self.root, bg="#1E293B", height=58)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header, text="Centro de Soporte Técnico TI",
            font=("Helvetica", 16, "bold"), bg="#1E293B", fg="#FFFFFF"
        ).pack(side="left", padx=20, pady=14)

        tk.Label(
            header, text="Sistema de Gestión de Órdenes y Activos",
            font=("Helvetica", 11), bg="#1E293B", fg="#94A3B8"
        ).pack(side="right", padx=20)

        # Contenedor de vistas (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=16, pady=14)

        self.tab_inicio = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_inicio, text="  Inicio  ")

        self.tab_tickets = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_tickets, text="  Órdenes de Servicio  ")

        self.tab_catalogos = ttk.Frame(self.notebook, style="Card.TFrame")
        self.notebook.add(self.tab_catalogos, text="  Clientes, Técnicos y Equipos  ")

        self.mapa_clientes = {}
        self.mapa_tecnicos = {}
        self.mapa_equipos = {}

        self.construir_vista_inicio()
        self.construir_pestana_tickets()
        self.construir_pestana_catalogos()
        self.refrescar_datos()

    # Definimos un estilo compatible con macOS
    def configurar_estilos(self):
        estilo = ttk.Style()
        estilo.theme_use("clam")

        estilo.configure("TNotebook", background="#F4F6F9", borderwidth=0)
        estilo.configure("TNotebook.Tab", font=("Helvetica", 10, "bold"), padding=[14, 7], background="#E2E8F0", foreground="#334155")
        estilo.map("TNotebook.Tab", background=[("selected", "#FFFFFF")], foreground=[("selected", "#0F172A")])

        estilo.configure("Card.TFrame", background="#FFFFFF")
        estilo.configure("Primary.TButton", font=("Helvetica", 10, "bold"), padding=[12, 6], background="#2563EB", foreground="#FFFFFF")
        estilo.map("Primary.TButton", background=[("active", "#1D4ED8")])

        estilo.configure("MenuBig.TButton", font=("Helvetica", 13, "bold"), padding=[24, 18], background="#2563EB", foreground="#FFFFFF")
        estilo.map("MenuBig.TButton", background=[("active", "#1D4ED8")])

        estilo.configure("MenuAlt.TButton", font=("Helvetica", 13, "bold"), padding=[24, 18], background="#0F172A", foreground="#FFFFFF")
        estilo.map("MenuAlt.TButton", background=[("active", "#334155")])

        estilo.configure("Secondary.TButton", font=("Helvetica", 10), padding=[10, 6], background="#E2E8F0", foreground="#1E293B")
        estilo.map("Secondary.TButton", background=[("active", "#CBD5E1")])

        estilo.configure("Danger.TButton", font=("Helvetica", 10, "bold"), padding=[12, 6], background="#DC2626", foreground="#FFFFFF")
        estilo.map("Danger.TButton", background=[("active", "#B91C1C")])

        estilo.configure("Treeview", font=("Helvetica", 10), rowheight=28, background="#FFFFFF", fieldbackground="#FFFFFF", foreground="#1E293B")
        estilo.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), background="#F1F5F9", foreground="#0F172A", relief="flat")

    # Creación de la pantalla de bienvenida con título y dos botones de navegación
    def construir_vista_inicio(self):
        contenedor = tk.Frame(self.tab_inicio, bg="#FFFFFF")
        contenedor.place(relx=0.5, rely=0.46, anchor="center")

        tk.Label(
            contenedor, text="Bienvenido al Centro de Soporte TI",
            font=("Helvetica", 26, "bold"), bg="#FFFFFF", fg="#0F172A"
        ).pack(pady=(0, 8))

        tk.Label(
            contenedor, text="Selecciona el módulo al que deseas ingresar para gestionar el servicio técnico",
            font=("Helvetica", 12), bg="#FFFFFF", fg="#64748B"
        ).pack(pady=(0, 34))

        fila_botones = tk.Frame(contenedor, bg="#FFFFFF")
        fila_botones.pack()

        ttk.Button(
            fila_botones,
            text="Órdenes de Servicio y Bitácoras",
            style="MenuBig.TButton",
            command=lambda: self.notebook.select(self.tab_tickets)
        ).pack(side="left", padx=16)

        ttk.Button(
            fila_botones,
            text="Clientes, Técnicos y Equipos",
            style="MenuAlt.TButton",
            command=lambda: self.notebook.select(self.tab_catalogos)
        ).pack(side="left", padx=16)

    # Creación de la vista órdenes de servicio y tabla de seguimiento
    def construir_pestana_tickets(self):
        top_nav = tk.Frame(self.tab_tickets, bg="#FFFFFF")
        top_nav.pack(fill="x", padx=16, pady=(10, 0))
        ttk.Button(
            top_nav, text="← Menú Principal", style="Secondary.TButton",
            command=lambda: self.notebook.select(self.tab_inicio)
        ).pack(side="left")

        f_tk = tk.LabelFrame(
            self.tab_tickets, text="Nueva Orden de Servicio",
            font=("Helvetica", 11, "bold"), bg="#FFFFFF", fg="#1E293B",
            padx=14, pady=10, bd=1, relief="solid"
        )
        f_tk.pack(fill="x", padx=16, pady=(10, 8))

        tk.Label(f_tk, text="Equipo:", bg="#FFFFFF", fg="#334155", font=("Helvetica", 10)).grid(row=0, column=0, sticky="w", pady=4)
        self.cmb_tk_equipo = ttk.Combobox(f_tk, state="readonly", width=36)
        self.cmb_tk_equipo.grid(row=0, column=1, padx=8)

        tk.Label(f_tk, text="Técnico asignado:", bg="#FFFFFF", fg="#334155", font=("Helvetica", 10)).grid(row=0, column=2, sticky="w", pady=4)
        self.cmb_tk_tecnico = ttk.Combobox(f_tk, state="readonly", width=26)
        self.cmb_tk_tecnico.grid(row=0, column=3, padx=8)

        tk.Label(f_tk, text="Valor estimado ($):", bg="#FFFFFF", fg="#334155", font=("Helvetica", 10)).grid(row=0, column=4, sticky="w", pady=4)
        self.ent_tk_costo = tk.Entry(f_tk, width=14, relief="solid", bd=1)
        self.ent_tk_costo.grid(row=0, column=5, padx=8)

        tk.Label(f_tk, text="Falla reportada:", bg="#FFFFFF", fg="#334155", font=("Helvetica", 10)).grid(row=1, column=0, sticky="w", pady=4)
        self.ent_tk_falla = tk.Entry(f_tk, width=38, relief="solid", bd=1)
        self.ent_tk_falla.grid(row=1, column=1, padx=8)

        tk.Label(f_tk, text="Revisión inicial:", bg="#FFFFFF", fg="#334155", font=("Helvetica", 10)).grid(row=1, column=2, sticky="w", pady=4)
        self.ent_tk_diag = tk.Entry(f_tk, width=28, relief="solid", bd=1)
        self.ent_tk_diag.grid(row=1, column=3, padx=8)

        f_chk = tk.Frame(f_tk, bg="#FFFFFF")
        f_chk.grid(row=2, column=0, columnspan=4, sticky="w", pady=(6, 2))
        tk.Label(f_chk, text="Estado físico al ingreso:", bg="#FFFFFF", fg="#475569", font=("Helvetica", 9, "bold")).pack(side="left", padx=(0, 8))

        self.var_enciende = tk.BooleanVar(value=True)
        self.var_pantalla = tk.BooleanVar(value=True)
        self.var_bateria = tk.BooleanVar(value=True)
        tk.Checkbutton(f_chk, text="Enciende", variable=self.var_enciende, bg="#FFFFFF").pack(side="left", padx=6)
        tk.Checkbutton(f_chk, text="Pantalla en buen estado", variable=self.var_pantalla, bg="#FFFFFF").pack(side="left", padx=6)
        tk.Checkbutton(f_chk, text="Batería funcional", variable=self.var_bateria, bg="#FFFFFF").pack(side="left", padx=6)

        ttk.Button(f_tk, text="Registrar Orden", style="Primary.TButton", command=self.accion_crear_ticket).grid(row=2, column=4, columnspan=2, sticky="e", padx=8, pady=4)

        f_tabla = tk.LabelFrame(
            self.tab_tickets, text="Historial de Órdenes de Servicio",
            font=("Helvetica", 11, "bold"), bg="#FFFFFF", fg="#1E293B",
            padx=12, pady=10, bd=1, relief="solid"
        )
        f_tabla.pack(fill="both", expand=True, padx=16, pady=8)

        self.tree_tickets = ttk.Treeview(f_tabla, show="headings", height=10)
        scroll_y = ttk.Scrollbar(f_tabla, orient="vertical", command=self.tree_tickets.yview)
        self.tree_tickets.configure(yscrollcommand=scroll_y.set)
        self.tree_tickets.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        f_btns = tk.Frame(self.tab_tickets, bg="#FFFFFF")
        f_btns.pack(fill="x", padx=16, pady=(4, 14))
        ttk.Button(f_btns, text="Actualizar Lista", style="Secondary.TButton", command=self.refrescar_datos).pack(side="left")
        ttk.Button(f_btns, text="Abrir Ficha Técnica y Bitácora", style="Primary.TButton", command=self.abrir_modal_expediente).pack(side="right")

    # Dibuja los formularios de registro de clientes, técnicos y equipos
    def construir_pestana_catalogos(self):
        top_nav = tk.Frame(self.tab_catalogos, bg="#FFFFFF")
        top_nav.pack(fill="x", padx=16, pady=(10, 0))
        ttk.Button(
            top_nav, text="← Menú Principal", style="Secondary.TButton",
            command=lambda: self.notebook.select(self.tab_inicio)
        ).pack(side="left")

        # Clientes
        f_cli = tk.LabelFrame(self.tab_catalogos, text="Registro de Clientes", font=("Helvetica", 11, "bold"), bg="#FFFFFF", fg="#1E293B", padx=14, pady=10, bd=1, relief="solid")
        f_cli.pack(fill="x", padx=16, pady=(10, 8))

        tk.Label(f_cli, text="Nombre completo:", bg="#FFFFFF", fg="#334155").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_cli_nombre = tk.Entry(f_cli, width=26, relief="solid", bd=1)
        self.ent_cli_nombre.grid(row=0, column=1, padx=8)

        tk.Label(f_cli, text="Documento:", bg="#FFFFFF", fg="#334155").grid(row=0, column=2, sticky="w", pady=4)
        self.ent_cli_doc = tk.Entry(f_cli, width=22, relief="solid", bd=1)
        self.ent_cli_doc.grid(row=0, column=3, padx=8)

        tk.Label(f_cli, text="Teléfono:", bg="#FFFFFF", fg="#334155").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_cli_tel = tk.Entry(f_cli, width=26, relief="solid", bd=1)
        self.ent_cli_tel.grid(row=1, column=1, padx=8)

        tk.Label(f_cli, text="Correo electrónico:", bg="#FFFFFF", fg="#334155").grid(row=1, column=2, sticky="w", pady=4)
        self.ent_cli_correo = tk.Entry(f_cli, width=26, relief="solid", bd=1)
        self.ent_cli_correo.grid(row=1, column=3, padx=8)

        ttk.Button(f_cli, text="Guardar Cliente", style="Primary.TButton", command=self.accion_guardar_cliente).grid(row=1, column=4, padx=14)

        # Técnicos
        f_tec = tk.LabelFrame(self.tab_catalogos, text="Registro de Técnicos", font=("Helvetica", 11, "bold"), bg="#FFFFFF", fg="#1E293B", padx=14, pady=10, bd=1, relief="solid")
        f_tec.pack(fill="x", padx=16, pady=8)

        tk.Label(f_tec, text="Nombre completo:", bg="#FFFFFF", fg="#334155").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_tec_nombre = tk.Entry(f_tec, width=26, relief="solid", bd=1)
        self.ent_tec_nombre.grid(row=0, column=1, padx=8)

        tk.Label(f_tec, text="Especialidad:", bg="#FFFFFF", fg="#334155").grid(row=0, column=2, sticky="w", pady=4)
        self.ent_tec_esp = tk.Entry(f_tec, width=22, relief="solid", bd=1)
        self.ent_tec_esp.grid(row=0, column=3, padx=8)

        tk.Label(f_tec, text="Usuario de acceso:", bg="#FFFFFF", fg="#334155").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_tec_user = tk.Entry(f_tec, width=26, relief="solid", bd=1)
        self.ent_tec_user.grid(row=1, column=1, padx=8)

        tk.Label(f_tec, text="Contraseña:", bg="#FFFFFF", fg="#334155").grid(row=1, column=2, sticky="w", pady=4)
        self.ent_tec_pass = tk.Entry(f_tec, width=22, show="*", relief="solid", bd=1)
        self.ent_tec_pass.grid(row=1, column=3, padx=8)

        ttk.Button(f_tec, text="Guardar Técnico", style="Primary.TButton", command=self.accion_guardar_tecnico).grid(row=1, column=4, padx=14)

        # Equipos
        f_eq = tk.LabelFrame(self.tab_catalogos, text="Registro de Equipos", font=("Helvetica", 11, "bold"), bg="#FFFFFF", fg="#1E293B", padx=14, pady=10, bd=1, relief="solid")
        f_eq.pack(fill="x", padx=16, pady=8)

        tk.Label(f_eq, text="Propietario:", bg="#FFFFFF", fg="#334155").grid(row=0, column=0, sticky="w", pady=4)
        self.cmb_eq_cliente = ttk.Combobox(f_eq, state="readonly", width=34)
        self.cmb_eq_cliente.grid(row=0, column=1, columnspan=2, sticky="w", padx=8)

        tk.Label(f_eq, text="Tipo de equipo:", bg="#FFFFFF", fg="#334155").grid(row=0, column=3, sticky="w", pady=4)
        self.cmb_eq_tipo = ttk.Combobox(f_eq, values=["Portátil", "PC Escritorio", "Impresora", "Servidor", "Otro"], state="readonly", width=18)
        self.cmb_eq_tipo.grid(row=0, column=4, padx=8)
        self.cmb_eq_tipo.set("Portátil")

        tk.Label(f_eq, text="Marca:", bg="#FFFFFF", fg="#334155").grid(row=1, column=0, sticky="w", pady=4)
        self.ent_eq_marca = tk.Entry(f_eq, width=20, relief="solid", bd=1)
        self.ent_eq_marca.grid(row=1, column=1, padx=8)

        tk.Label(f_eq, text="Modelo:", bg="#FFFFFF", fg="#334155").grid(row=1, column=2, sticky="w", pady=4)
        self.ent_eq_modelo = tk.Entry(f_eq, width=20, relief="solid", bd=1)
        self.ent_eq_modelo.grid(row=1, column=3, padx=8)

        tk.Label(f_eq, text="Número de serie:", bg="#FFFFFF", fg="#334155").grid(row=1, column=4, sticky="w", pady=4)
        self.ent_eq_serial = tk.Entry(f_eq, width=18, relief="solid", bd=1)
        self.ent_eq_serial.grid(row=1, column=5, padx=8)

        ttk.Button(f_eq, text="Guardar Equipo", style="Primary.TButton", command=self.accion_guardar_equipo).grid(row=2, column=5, pady=8, padx=8, sticky="e")

    # Actualiza las listas desplegables y recarga la tabla de órdenes
    def refrescar_datos(self):
        self.mapa_clientes.clear()
        op_cli = []
        for c in listar_clientes():
            lbl = f"{c['nombre_cli']} — Doc. {c['documento_cli']}"
            self.mapa_clientes[lbl] = c["id_cliente"]
            op_cli.append(lbl)
        self.cmb_eq_cliente["values"] = op_cli
        if op_cli:
            self.cmb_eq_cliente.current(0)

        self.mapa_tecnicos.clear()
        op_tec = []
        for t in listar_tecnicos():
            lbl = f"{t['nombre_tec']} ({t['especialidad']})"
            self.mapa_tecnicos[lbl] = t["id_tecnico"]
            op_tec.append(lbl)
        self.cmb_tk_tecnico["values"] = op_tec
        if op_tec:
            self.cmb_tk_tecnico.current(0)

        self.mapa_equipos.clear()
        op_eq = []
        for e in listar_equipos():
            lbl = f"{e['tipo_equipo']} {e['marca']} [{e['serial_number']}] — {e['nombre_cli']}"
            self.mapa_equipos[lbl] = e["id_equipo"]
            op_eq.append(lbl)
        self.cmb_tk_equipo["values"] = op_eq
        if op_eq:
            self.cmb_tk_equipo.current(0)

        tickets = listar_todos_tickets()
        self.tree_tickets.delete(*self.tree_tickets.get_children())
        if tickets:
            cols = list(tickets[0].keys())
            self.tree_tickets["columns"] = cols
            for col in cols:
                self.tree_tickets.heading(col, text=col.replace("_", " ").title())
                self.tree_tickets.column(col, width=125, anchor="w")
            for row in tickets:
                self.tree_tickets.insert("", tk.END, values=[row[c] for c in cols])

    # Valida y registra un nuevo cliente
    def accion_guardar_cliente(self):
        nombre, doc = self.ent_cli_nombre.get().strip(), self.ent_cli_doc.get().strip()
        tel, correo = self.ent_cli_tel.get().strip(), self.ent_cli_correo.get().strip()
        if not nombre or not doc:
            messagebox.showwarning("Datos incompletos", "Ingresa el nombre y el documento del cliente.")
            return
        nuevo_id = registrar_cliente(nombre, doc, tel, correo)
        if nuevo_id:
            messagebox.showinfo("Registro exitoso", f"Cliente guardado correctamente (Código #{nuevo_id}).")
            for ent in (self.ent_cli_nombre, self.ent_cli_doc, self.ent_cli_tel, self.ent_cli_correo):
                ent.delete(0, tk.END)
            self.refrescar_datos()
        else:
            messagebox.showerror("Error de registro", "No se pudo guardar el cliente.")

    # Valida y registra un nuevo técnico
    def accion_guardar_tecnico(self):
        nombre, esp = self.ent_tec_nombre.get().strip(), self.ent_tec_esp.get().strip()
        user, clave = self.ent_tec_user.get().strip(), self.ent_tec_pass.get().strip()
        if not nombre or not user or not clave:
            messagebox.showwarning("Datos incompletos", "Nombre, usuario y contraseña son obligatorios.")
            return
        nuevo_id = registrar_tecnico(nombre, esp, user, clave)
        if nuevo_id:
            messagebox.showinfo("Registro exitoso", f"Técnico guardado correctamente (Código #{nuevo_id}).")
            for ent in (self.ent_tec_nombre, self.ent_tec_esp, self.ent_tec_user, self.ent_tec_pass):
                ent.delete(0, tk.END)
            self.refrescar_datos()
        else:
            messagebox.showerror("Error de registro", "No se pudo guardar el técnico.")

    # Valida y registra un equipo asociado a su propietario
    def accion_guardar_equipo(self):
        sel_cli = self.cmb_eq_cliente.get()
        tipo, marca = self.cmb_eq_tipo.get(), self.ent_eq_marca.get().strip()
        modelo, serial = self.ent_eq_modelo.get().strip(), self.ent_eq_serial.get().strip()
        if not sel_cli or not marca or not serial:
            messagebox.showwarning("Datos incompletos", "Selecciona un propietario e ingresa la marca y el serial.")
            return
        nuevo_id = registrar_equipo(tipo, marca, modelo, serial, self.mapa_clientes[sel_cli])
        if nuevo_id:
            messagebox.showinfo("Registro exitoso", f"Equipo guardado correctamente (Código #{nuevo_id}).")
            for ent in (self.ent_eq_marca, self.ent_eq_modelo, self.ent_eq_serial):
                ent.delete(0, tk.END)
            self.refrescar_datos()
        else:
            messagebox.showerror("Error de registro", "No se pudo guardar el equipo.")

    # Registra la orden de servicio con su checklist de recepción
    def accion_crear_ticket(self):
        sel_eq, sel_tec = self.cmb_tk_equipo.get(), self.cmb_tk_tecnico.get()
        falla, diag = self.ent_tk_falla.get().strip(), self.ent_tk_diag.get().strip()
        try:
            costo = float(self.ent_tk_costo.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Valor inválido", "El valor estimado debe ser un número.")
            return

        if not sel_eq or not sel_tec or not falla:
            messagebox.showwarning("Datos incompletos", "Selecciona el equipo, el técnico y describe la falla.")
            return

        checklist = {
            "enciende": self.var_enciende.get(),
            "pantalla_ok": self.var_pantalla.get(),
            "bateria_ok": self.var_bateria.get()
        }
        id_ticket = crear_ticket_completo(
            falla=falla, costo=costo,
            id_equipo=self.mapa_equipos[sel_eq],
            id_tecnico=self.mapa_tecnicos[sel_tec],
            diagnostico_inicial=diag or "Pendiente de diagnóstico detallado",
            checklist=checklist
        )
        if id_ticket:
            messagebox.showinfo("Orden creada", f"Orden de servicio #{id_ticket} registrada exitosamente.")
            for ent in (self.ent_tk_falla, self.ent_tk_diag, self.ent_tk_costo):
                ent.delete(0, tk.END)
            self.refrescar_datos()
        else:
            messagebox.showerror("Error", "No se pudo registrar la orden de servicio.")

    # Recorre dinámicamente todas las secciones del expediente y las formatea sin JSON crudo
    def formatear_ficha_legible(self, expediente):
        if not expediente or not isinstance(expediente, dict):
            return "No se encontró información para esta orden."

        lineas = ["============================================================"]
        lineas.append("                  RESUMEN DE ORDEN DE SERVICIO")
        lineas.append("============================================================")

        for seccion, contenido in expediente.items():
            if seccion == "_id":
                continue

            if isinstance(contenido, dict):
                titulo = seccion.replace("_", " ").upper()
                lineas.append(f"\n[ {titulo} ]")
                for k, v in contenido.items():
                    if k == "_id":
                        continue
                    etiqueta = k.replace("_", " ").capitalize()
                    if isinstance(v, dict):
                        detalle = ", ".join(
                            f"{sk.replace('_', ' ')}: {'Sí' if sv is True else 'No' if sv is False else sv}"
                            for sk, sv in v.items()
                        )
                        lineas.append(f"  • {etiqueta}: {detalle}")
                    elif isinstance(v, list):
                        lineas.append(f"  • {etiqueta}:")
                        if not v:
                            lineas.append("      - Ninguno registrado")
                        for item in v:
                            if isinstance(item, dict):
                                fecha = item.get("fecha", "")
                                nota = item.get("nota") or item.get("accion") or str(item)
                                lineas.append(f"      - [{fecha}] {nota}" if fecha else f"      - {nota}")
                            else:
                                lineas.append(f"      - {item}")
                    else:
                        lineas.append(f"  • {etiqueta}: {v}")
            else:
                etiqueta = seccion.replace("_", " ").capitalize()
                lineas.append(f"  • {etiqueta}: {contenido}")

        return "\n".join(lineas)

    # Abre la ventana de detalle con vista legible, registro de avances y cierre de orden
    def abrir_modal_expediente(self):
        seleccion = self.tree_tickets.selection()
        if not seleccion:
            messagebox.showwarning("Selección requerida", "Selecciona una orden de servicio de la tabla.")
            return

        valores = self.tree_tickets.item(seleccion[0], "values")
        id_ticket = int(valores[0])
        expediente = consultar_expediente_ticket(id_ticket)

        modal = tk.Toplevel(self.root)
        modal.title(f"Ficha Técnica — Orden de Servicio #{id_ticket}")
        modal.geometry("760x600")
        modal.configure(bg="#F4F6F9")
        modal.grab_set()

        txt_exp = tk.Text(modal, height=19, width=88, font=("Helvetica", 10), bg="#FFFFFF", fg="#1E293B", padx=14, pady=12, relief="solid", bd=1)
        txt_exp.pack(padx=14, pady=(14, 8), fill="both", expand=True)
        txt_exp.insert(tk.END, self.formatear_ficha_legible(expediente))
        txt_exp.config(state="disabled")

        f_av = tk.LabelFrame(modal, text="Registrar Avance o Repuesto", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#1E293B", padx=12, pady=8, bd=1, relief="solid")
        f_av.pack(fill="x", padx=14, pady=4)

        tk.Label(f_av, text="Descripción del avance:", bg="#FFFFFF", fg="#334155").grid(row=0, column=0, sticky="w")
        ent_nota = tk.Entry(f_av, width=34, relief="solid", bd=1)
        ent_nota.grid(row=0, column=1, padx=6)

        tk.Label(f_av, text="Repuesto (opcional):", bg="#FFFFFF", fg="#334155").grid(row=0, column=2, sticky="w")
        ent_rep = tk.Entry(f_av, width=18, relief="solid", bd=1)
        ent_rep.grid(row=0, column=3, padx=6)

        def guardar_avance():
            nota = ent_nota.get().strip()
            if not nota:
                messagebox.showwarning("Campo vacío", "Escribe una descripción del avance.", parent=modal)
                return
            ok = agregar_avance_bitacora(id_ticket, nota, ent_rep.get().strip())
            if ok:
                messagebox.showinfo("Avance guardado", "La bitácora se actualizó correctamente.", parent=modal)
                modal.destroy()
                self.abrir_modal_expediente()
            else:
                messagebox.showerror("Error", "No se pudo actualizar la bitácora.", parent=modal)

        ttk.Button(f_av, text="Guardar Avance", style="Primary.TButton", command=guardar_avance).grid(row=0, column=4, padx=6)

        f_cer = tk.LabelFrame(modal, text="Finalizar y Cerrar Orden de Servicio", font=("Helvetica", 10, "bold"), bg="#FFFFFF", fg="#1E293B", padx=12, pady=8, bd=1, relief="solid")
        f_cer.pack(fill="x", padx=14, pady=(4, 14))

        tk.Label(f_cer, text="Solución aplicada:", bg="#FFFFFF", fg="#334155").grid(row=0, column=0, sticky="w")
        ent_sol = tk.Entry(f_cer, width=52, relief="solid", bd=1)
        ent_sol.grid(row=0, column=1, padx=6)

        def ejecutar_cierre():
            sol = ent_sol.get().strip()
            if not sol:
                messagebox.showwarning("Campo vacío", "Describe la solución final antes de cerrar la orden.", parent=modal)
                return
            if cerrar_ticket(id_ticket, sol):
                messagebox.showinfo("Orden cerrada", f"La orden #{id_ticket} ha sido cerrada.", parent=modal)
                modal.destroy()
                self.refrescar_datos()
            else:
                messagebox.showerror("Error", "No se pudo cerrar la orden.", parent=modal)

        ttk.Button(f_cer, text="Cerrar Orden", style="Danger.TButton", command=ejecutar_cierre).grid(row=0, column=2, padx=6)
