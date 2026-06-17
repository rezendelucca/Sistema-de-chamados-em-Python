import configparser
import os
import sys
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from database.connection import DatabaseConnection
from exceptions.chamado_invalido_exception import ChamadoInvalidoException
from models.chamado import Chamado
from services.chamado_service import ChamadoService

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
SENHA_ACESSO = '1234'


# ---------------------------------------------------------------------------
# Config helpers
# ---------------------------------------------------------------------------

def ler_config() -> dict:
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_PATH, encoding='utf-8')
    db = cfg['database'] if 'database' in cfg else {}
    return {
        'host':     db.get('host',     'localhost'),
        'port':     db.get('port',     '5432'),
        'database': db.get('database', 'ticketflow'),
        'user':     db.get('user',     'postgres'),
        'password': db.get('password', ''),
    }


def salvar_config(valores: dict):
    cfg = configparser.ConfigParser()
    cfg['database'] = valores
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        cfg.write(f)


# ---------------------------------------------------------------------------
# Tela de conexao
# ---------------------------------------------------------------------------

class TelaConexao:
    def __init__(self):
        self.sucesso = False
        self.janela  = tk.Tk()
        self.janela.title("TicketFlow - Conexao")
        self.janela.geometry("460x380")
        self.janela.resizable(False, False)
        self._centralizar(self.janela)
        self._construir()
        self.janela.mainloop()

    @staticmethod
    def _centralizar(win):
        win.update_idletasks()
        w = win.winfo_width()  or 460
        h = win.winfo_height() or 380
        x = (win.winfo_screenwidth()  // 2) - (w // 2)
        y = (win.winfo_screenheight() // 2) - (h // 2)
        win.geometry(f"+{x}+{y}")

    def _construir(self):
        cfg = ler_config()

        # --- Header ---
        header = tk.Frame(self.janela, bg='#4a6cf7', height=72)
        header.pack(fill='x')
        header.pack_propagate(False)
        tk.Label(header, text="TicketFlow", bg='#4a6cf7', fg='white',
                 font=('Segoe UI', 22, 'bold')).pack(expand=True)

        # --- Formulario ---
        frame = ttk.Frame(self.janela, padding=(35, 18))
        frame.pack(fill='both', expand=True)

        self.campos = {}
        linhas = [
            ('Host:',    'host',     False, ''),
            ('Banco:',   'database', False, ''),
            ('Usuario:', 'user',     False, ''),
            ('Senha:',   'password', True,  ''),
        ]

        for i, (label, key, senha, _) in enumerate(linhas):
            ttk.Label(frame, text=label, width=11, anchor='w').grid(
                row=i, column=0, sticky='w', pady=7)
            e = ttk.Entry(frame, width=32, show='*' if senha else '')
            e.insert(0, cfg.get(key, ''))
            e.grid(row=i, column=1, sticky='ew', padx=(8, 0), pady=7)
            self.campos[key] = e

        # Porta destacada
        tk.Label(frame, text='Porta:', width=11, anchor='w',
                 fg='#4a6cf7', font=('Segoe UI', 9, 'bold')).grid(
            row=4, column=0, sticky='w', pady=7)

        porta_frame = ttk.Frame(frame)
        porta_frame.grid(row=4, column=1, sticky='ew', padx=(8, 0), pady=7)

        self.campos['port'] = ttk.Entry(porta_frame, width=8,
                                        font=('Segoe UI', 10, 'bold'))
        self.campos['port'].insert(0, cfg.get('port', '5432'))
        self.campos['port'].pack(side='left')

        tk.Label(porta_frame, text='  ← compartilhe esta porta para conexoes externas',
                 fg='#4a6cf7', font=('Segoe UI', 8, 'italic')).pack(side='left')

        frame.columnconfigure(1, weight=1)

        # --- Botoes ---
        btn_frame = ttk.Frame(self.janela, padding=(35, 0, 35, 18))
        btn_frame.pack(fill='x')
        ttk.Button(btn_frame, text='Conectar', command=self._conectar).pack(side='right', padx=(6, 0))
        ttk.Button(btn_frame, text='Sair',     command=sys.exit).pack(side='right')

        self.janela.bind('<Return>', lambda _: self._conectar())

    def _conectar(self):
        host     = self.campos['host'].get().strip()     or 'localhost'
        database = self.campos['database'].get().strip() or 'ticketflow'
        user     = self.campos['user'].get().strip()     or 'postgres'
        password = self.campos['password'].get()
        port_str = self.campos['port'].get().strip()     or '5432'

        if password != SENHA_ACESSO:
            messagebox.showerror("Erro de Conexao", "Senha incorreta.", parent=self.janela)
            return

        try:
            port = int(port_str)
        except ValueError:
            messagebox.showerror("Erro", "Porta invalida.", parent=self.janela)
            return

        try:
            DatabaseConnection.get_instance().connect(
                host=host, database=database, user=user,
                password=password, port=port
            )
            salvar_config({'host': host, 'port': str(port),
                           'database': database, 'user': user, 'password': password})
            self.sucesso = True
            self.janela.quit()
        except Exception as e:
            try:
                msg = str(e)
            except Exception:
                msg = "Verifique os dados de conexao."
            messagebox.showerror("Erro de Conexao", msg, parent=self.janela)


# ---------------------------------------------------------------------------
# Janela principal
# ---------------------------------------------------------------------------

class AppPrincipal:
    COLUNAS  = ('ID', 'Tipo', 'Titulo', 'Prioridade', 'Status', 'Solicitante', 'Abertura')
    LARGURAS = {'ID': 45, 'Tipo': 115, 'Titulo': 210, 'Prioridade': 82,
                'Status': 108, 'Solicitante': 145, 'Abertura': 128}

    def __init__(self):
        self.service = ChamadoService()
        self.janela  = tk.Tk()
        self.janela.title("TicketFlow - Sistema de Gestao de Chamados")
        self.janela.geometry("1060x640")
        self.janela.minsize(800, 500)

        # Tema
        style = ttk.Style()
        try:
            style.theme_use('vista')
        except tk.TclError:
            style.theme_use('clam')

        self._construir()
        self._atualizar_lista()
        self.janela.mainloop()

    # ------------------------------------------------------------------ UI

    def _construir(self):
        self._toolbar()
        self._barra_filtros()
        self._treeview()
        self._statusbar()

    def _toolbar(self):
        bar = tk.Frame(self.janela, bg='#2d2d44', padx=8, pady=8)
        bar.pack(fill='x')

        botoes = [
            ('+ Abrir Chamado', '#27ae60', self._abrir_chamado),
            ('Atualizar',       '#2980b9', self._atualizar_chamado),
            ('Encerrar',        '#e67e22', self._encerrar_chamado),
            ('Excluir',         '#c0392b', self._excluir_chamado),
            ('Relatorio',       '#8e44ad', self._relatorio),
        ]
        for txt, cor, cmd in botoes:
            tk.Button(bar, text=txt, command=cmd, bg=cor, fg='white',
                      relief='flat', padx=12, pady=6, cursor='hand2',
                      font=('Segoe UI', 9, 'bold'),
                      activebackground=cor, activeforeground='white'
                      ).pack(side='left', padx=3)

    def _barra_filtros(self):
        bar = tk.Frame(self.janela, bg='#f0f0f5', padx=8, pady=5)
        bar.pack(fill='x')

        tk.Label(bar, text='Filtrar:', bg='#f0f0f5',
                 font=('Segoe UI', 9, 'bold')).pack(side='left', padx=(0, 6))

        filtros = [
            ('Todos',        '#555555', lambda: self._atualizar_lista()),
            ('Aberto',       '#27ae60', lambda: self._filtrar_status('ABERTO')),
            ('Em Andamento', '#2980b9', lambda: self._filtrar_status('EM_ANDAMENTO')),
            ('Encerrado',    '#7f8c8d', lambda: self._filtrar_status('ENCERRADO')),
            ('Alta / Critica','#c0392b', self._filtrar_alta),
        ]
        for txt, cor, cmd in filtros:
            tk.Button(bar, text=txt, command=cmd, bg=cor, fg='white',
                      relief='flat', padx=8, pady=3, cursor='hand2',
                      font=('Segoe UI', 8)).pack(side='left', padx=2)

        # Busca rapida por ID
        tk.Label(bar, text='   ID:', bg='#f0f0f5').pack(side='left')
        self._busca_id = ttk.Entry(bar, width=6)
        self._busca_id.pack(side='left', padx=(2, 0))
        ttk.Button(bar, text='Ver', command=self._buscar_id).pack(side='left', padx=2)
        self._busca_id.bind('<Return>', lambda _: self._buscar_id())

        # Busca por departamento
        tk.Label(bar, text='  Depto:', bg='#f0f0f5').pack(side='left')
        self._busca_depto = ttk.Entry(bar, width=12)
        self._busca_depto.pack(side='left', padx=(2, 0))
        ttk.Button(bar, text='Buscar', command=self._filtrar_depto).pack(side='left', padx=2)
        self._busca_depto.bind('<Return>', lambda _: self._filtrar_depto())

    def _treeview(self):
        frame = ttk.Frame(self.janela)
        frame.pack(fill='both', expand=True, padx=8, pady=(4, 0))

        self.tree = ttk.Treeview(frame, columns=self.COLUNAS, show='headings', selectmode='browse')
        for col in self.COLUNAS:
            anchor = 'center' if col in ('ID', 'Prioridade', 'Status', 'Abertura') else 'w'
            self.tree.heading(col, text=col, command=lambda c=col: self._ordenar(c))
            self.tree.column(col, width=self.LARGURAS[col], anchor=anchor)

        self.tree.tag_configure('CRITICA',   background='#fde8e8')
        self.tree.tag_configure('ALTA',      background='#fef3e2')
        self.tree.tag_configure('ENCERRADO', background='#f0f0f0', foreground='#999999')
        self.tree.tag_configure('CANCELADO', background='#f5f5f5', foreground='#aaaaaa')

        sy = ttk.Scrollbar(frame, orient='vertical',   command=self.tree.yview)
        sx = ttk.Scrollbar(frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)

        sy.pack(side='right',  fill='y')
        sx.pack(side='bottom', fill='x')
        self.tree.pack(fill='both', expand=True)

        self.tree.bind('<Double-1>', lambda _: self._ver_detalhes())

        self._label_total = tk.Label(self.janela, text='', anchor='w',
                                     font=('Segoe UI', 8), fg='#555', bg='white')
        self._label_total.pack(fill='x', padx=10)

    def _statusbar(self):
        cfg = ler_config()
        info = (f"  Conectado: {cfg['user']}@{cfg['host']}:{cfg['port']}"
                f"   |   Banco: {cfg['database']}"
                f"   |   Duplo clique numa linha para ver detalhes")
        bar = tk.Frame(self.janela, bg='#2d2d44', height=24)
        bar.pack(fill='x', side='bottom')
        tk.Label(bar, text=info, bg='#2d2d44', fg='#aaaaaa',
                 font=('Segoe UI', 8)).pack(side='left')

    # ------------------------------------------------------------------ Lista

    def _atualizar_lista(self, chamados=None):
        if chamados is None:
            try:
                chamados = self.service.listar_chamados()
            except Exception as e:
                messagebox.showerror("Erro", str(e))
                return

        self.tree.delete(*self.tree.get_children())
        for c in chamados:
            tipo = type(c).__name__.replace('Chamado', '')
            tag  = c.status if c.status in ('ENCERRADO', 'CANCELADO') else c.prioridade
            self.tree.insert('', 'end', tags=(tag,), values=(
                c.id, tipo, c.titulo[:50], c.prioridade, c.status,
                c.usuario.nome, c.data_abertura.strftime('%d/%m/%Y %H:%M')
            ))

        self._label_total.config(text=f"  {len(chamados)} chamado(s) encontrado(s)")

    def _filtrar_status(self, status):
        try:
            self._atualizar_lista(self.service.buscar_por_status(status))
        except ChamadoInvalidoException as e:
            messagebox.showerror("Erro", str(e))

    def _filtrar_alta(self):
        try:
            lista = (self.service.buscar_por_prioridade('CRITICA') +
                     self.service.buscar_por_prioridade('ALTA'))
            self._atualizar_lista(lista)
        except ChamadoInvalidoException as e:
            messagebox.showerror("Erro", str(e))

    def _filtrar_depto(self):
        depto = self._busca_depto.get().strip()
        if not depto:
            return
        self._atualizar_lista(self.service.buscar_por_departamento(depto))

    def _ordenar(self, col):
        dados = [(self.tree.set(i, col), i) for i in self.tree.get_children()]
        dados.sort()
        for idx, (_, item) in enumerate(dados):
            self.tree.move(item, '', idx)

    # ------------------------------------------------------------------ Detalhes

    def _id_selecionado(self, titulo_dialog: str):
        """Retorna o ID do chamado selecionado na lista, ou pede via dialog."""
        sel = self.tree.selection()
        if sel:
            return int(self.tree.item(sel[0])['values'][0])
        id_str = simpledialog.askstring(titulo_dialog, "ID do chamado:", parent=self.janela)
        if not id_str:
            return None
        try:
            return int(id_str)
        except ValueError:
            messagebox.showerror("Erro", "ID invalido.")
            return None

    def _buscar_id(self):
        id_str = self._busca_id.get().strip()
        if not id_str:
            return
        try:
            chamado = self.service.buscar_chamado(int(id_str))
            self._dialog_detalhes(chamado)
        except (ChamadoInvalidoException, ValueError) as e:
            messagebox.showerror("Erro", str(e))

    def _ver_detalhes(self):
        sel = self.tree.selection()
        if not sel:
            return
        id_c = int(self.tree.item(sel[0])['values'][0])
        try:
            self._dialog_detalhes(self.service.buscar_chamado(id_c))
        except ChamadoInvalidoException as e:
            messagebox.showerror("Erro", str(e))

    def _dialog_detalhes(self, chamado):
        top = tk.Toplevel(self.janela)
        top.title(f"Chamado #{chamado.id}")
        top.geometry("500x310")
        top.resizable(False, False)
        top.grab_set()

        tipo = type(chamado).__name__.replace('Chamado', '').upper()
        extra = ''
        for attr, label in [('categoria_ti',  'Categoria TI  '),
                             ('cargo_afetado', 'Cargo Afetado '),
                             ('centro_custo',  'Centro Custo  '),
                             ('local_instalacao', 'Local Instal.')]:
            val = getattr(chamado, attr, None)
            if val:
                extra = f"  {label}: {val}\n"
                break

        conteudo = (
            f"{'='*46}\n"
            f"  CHAMADO {tipo}  #{chamado.id}\n"
            f"{'='*46}\n"
            f"  Titulo     : {chamado.titulo}\n"
            f"  Descricao  : {chamado.descricao}\n"
            f"{extra}"
            f"  Prioridade : {chamado.prioridade}\n"
            f"  Status     : {chamado.status}\n"
            f"  Solicitante: {chamado.usuario.nome} ({chamado.usuario.departamento})\n"
            f"  Abertura   : {chamado.data_abertura.strftime('%d/%m/%Y %H:%M')}\n"
            f"{'='*46}"
        )

        txt = tk.Text(top, wrap='word', padx=14, pady=12,
                      font=('Consolas', 10), relief='flat', bg='#fafafa')
        txt.pack(fill='both', expand=True)
        txt.insert('1.0', conteudo)
        txt.config(state='disabled')

        ttk.Button(top, text='Fechar', command=top.destroy).pack(pady=8)

    # ------------------------------------------------------------------ Abrir chamado

    def _abrir_chamado(self):
        top = tk.Toplevel(self.janela)
        top.title("Abrir Novo Chamado")
        top.geometry("510x470")
        top.resizable(False, False)
        top.grab_set()

        frame = ttk.Frame(top, padding=22)
        frame.pack(fill='both', expand=True)

        def row(lbl, widget, r):
            ttk.Label(frame, text=lbl, anchor='w').grid(row=r, column=0, sticky='w', pady=7)
            widget.grid(row=r, column=1, sticky='ew', padx=(10, 0), pady=7)

        tipo_var = tk.StringVar(value='TI')
        row('Tipo:', ttk.Combobox(frame, textvariable=tipo_var,
            values=['TI', 'RH', 'FINANCEIRO', 'INFRAESTRUTURA'],
            state='readonly', width=31), 0)

        usuarios   = self.service.listar_usuarios()
        usuario_map = {f"[{u.id}] {u.nome}  ({u.departamento})": u.id for u in usuarios}
        usuario_var = tk.StringVar()
        usuario_cb  = ttk.Combobox(frame, textvariable=usuario_var,
                                    values=list(usuario_map.keys()),
                                    state='readonly', width=31)
        if usuarios:
            usuario_cb.set(list(usuario_map.keys())[0])
        row('Solicitante:', usuario_cb, 1)

        titulo_e = ttk.Entry(frame, width=33)
        row('Titulo:', titulo_e, 2)

        desc_t = tk.Text(frame, height=4, width=33, wrap='word', relief='solid', bd=1)
        row('Descricao:', desc_t, 3)

        prio_var = tk.StringVar(value='MEDIA')
        row('Prioridade:', ttk.Combobox(frame, textvariable=prio_var,
            values=Chamado.PRIORIDADES_VALIDAS, state='readonly', width=31), 4)

        _extra_labels = {'TI': 'Categoria TI:', 'RH': 'Cargo Afetado:',
                         'FINANCEIRO': 'Centro Custo:', 'INFRAESTRUTURA': 'Local Instal.:'}
        _extra_keys   = {'TI': 'categoria_ti', 'RH': 'cargo_afetado',
                         'FINANCEIRO': 'centro_custo', 'INFRAESTRUTURA': 'local_instalacao'}
        extra_lbl_var = tk.StringVar(value='Categoria TI:')
        extra_lbl_w   = ttk.Label(frame, textvariable=extra_lbl_var, anchor='w')
        extra_lbl_w.grid(row=5, column=0, sticky='w', pady=7)
        extra_e = ttk.Entry(frame, width=33)
        extra_e.grid(row=5, column=1, sticky='ew', padx=(10, 0), pady=7)

        tipo_var.trace_add('write', lambda *_: extra_lbl_var.set(
            _extra_labels.get(tipo_var.get(), 'Campo extra:')))

        frame.columnconfigure(1, weight=1)

        def salvar():
            try:
                uid = usuario_map.get(usuario_var.get())
                if uid is None:
                    messagebox.showerror("Erro", "Selecione um solicitante.", parent=top)
                    return
                tipo = tipo_var.get()
                c = self.service.abrir_chamado(
                    tipo, titulo_e.get(), desc_t.get('1.0', 'end'),
                    prio_var.get(), uid,
                    **{_extra_keys[tipo]: extra_e.get().strip() or None}
                )
                messagebox.showinfo("Sucesso", f"Chamado #{c.id} aberto com sucesso!", parent=top)
                top.destroy()
                self._atualizar_lista()
            except ChamadoInvalidoException as e:
                messagebox.showerror("Erro", str(e), parent=top)

        bf = ttk.Frame(frame)
        bf.grid(row=6, column=0, columnspan=2, pady=12)
        ttk.Button(bf, text='Salvar',   command=salvar).pack(side='left', padx=5)
        ttk.Button(bf, text='Cancelar', command=top.destroy).pack(side='left')
        top.bind('<Return>', lambda _: salvar())

    # ------------------------------------------------------------------ Atualizar

    def _atualizar_chamado(self):
        id_c = self._id_selecionado("Atualizar Chamado")
        if id_c is None:
            return
        try:
            chamado = self.service.buscar_chamado(id_c)
        except ChamadoInvalidoException as e:
            messagebox.showerror("Erro", str(e))
            return

        top = tk.Toplevel(self.janela)
        top.title(f"Atualizar Chamado #{chamado.id}")
        top.geometry("510x340")
        top.resizable(False, False)
        top.grab_set()

        frame = ttk.Frame(top, padding=22)
        frame.pack(fill='both', expand=True)

        ttk.Label(frame, text='Titulo:').grid(row=0, column=0, sticky='w', pady=7)
        titulo_e = ttk.Entry(frame, width=36)
        titulo_e.insert(0, chamado.titulo)
        titulo_e.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=7)

        ttk.Label(frame, text='Descricao:').grid(row=1, column=0, sticky='nw', pady=7)
        desc_t = tk.Text(frame, height=4, width=36, wrap='word', relief='solid', bd=1)
        desc_t.insert('1.0', chamado.descricao)
        desc_t.grid(row=1, column=1, sticky='ew', padx=(10, 0), pady=7)

        ttk.Label(frame, text='Prioridade:').grid(row=2, column=0, sticky='w', pady=7)
        prio_var = tk.StringVar(value=chamado.prioridade)
        ttk.Combobox(frame, textvariable=prio_var, values=Chamado.PRIORIDADES_VALIDAS,
                     state='readonly', width=34).grid(row=2, column=1, sticky='ew', padx=(10, 0), pady=7)

        ttk.Label(frame, text='Status:').grid(row=3, column=0, sticky='w', pady=7)
        status_var = tk.StringVar(value=chamado.status)
        ttk.Combobox(frame, textvariable=status_var, values=Chamado.STATUS_VALIDOS,
                     state='readonly', width=34).grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=7)

        frame.columnconfigure(1, weight=1)

        def salvar():
            try:
                self.service.atualizar_chamado(
                    chamado.id,
                    titulo=titulo_e.get().strip(),
                    descricao=desc_t.get('1.0', 'end').strip(),
                    prioridade=prio_var.get()
                )
                if status_var.get() != chamado.status:
                    self.service.alterar_status(chamado.id, status_var.get())
                messagebox.showinfo("Sucesso", f"Chamado #{chamado.id} atualizado!", parent=top)
                top.destroy()
                self._atualizar_lista()
            except ChamadoInvalidoException as e:
                messagebox.showerror("Erro", str(e), parent=top)

        bf = ttk.Frame(frame)
        bf.grid(row=4, column=0, columnspan=2, pady=12)
        ttk.Button(bf, text='Salvar',   command=salvar).pack(side='left', padx=5)
        ttk.Button(bf, text='Cancelar', command=top.destroy).pack(side='left')

    # ------------------------------------------------------------------ Encerrar / Excluir

    def _encerrar_chamado(self):
        id_c = self._id_selecionado("Encerrar Chamado")
        if id_c is None:
            return
        try:
            chamado = self.service.buscar_chamado(id_c)
            if messagebox.askyesno("Encerrar",
                                   f"Encerrar o chamado #{chamado.id}?\n\n\"{chamado.titulo}\""):
                self.service.encerrar_chamado(chamado.id)
                messagebox.showinfo("Sucesso", f"Chamado #{chamado.id} encerrado!")
                self._atualizar_lista()
        except ChamadoInvalidoException as e:
            messagebox.showerror("Erro", str(e))

    def _excluir_chamado(self):
        id_c = self._id_selecionado("Excluir Chamado")
        if id_c is None:
            return
        try:
            chamado = self.service.buscar_chamado(id_c)
            if messagebox.askyesno("Excluir",
                                   f"Excluir permanentemente o chamado #{chamado.id}?\n\n"
                                   f"\"{chamado.titulo}\"\n\nEsta acao nao pode ser desfeita.",
                                   icon='warning'):
                self.service.excluir_chamado(chamado.id)
                messagebox.showinfo("Sucesso", f"Chamado #{chamado.id} excluido!")
                self._atualizar_lista()
        except ChamadoInvalidoException as e:
            messagebox.showerror("Erro", str(e))

    # ------------------------------------------------------------------ Relatorio

    def _relatorio(self):
        try:
            rel = self.service.gerar_relatorio()
        except Exception as e:
            messagebox.showerror("Erro", str(e))
            return

        top = tk.Toplevel(self.janela)
        top.title("Relatorio de Chamados")
        top.geometry("560X450")
        top.grab_set()

        nb = ttk.Notebook(top)
        nb.pack(fill='both', expand=True, padx=10, pady=10)

        def aba(titulo, dados, c1, c2):
            f = ttk.Frame(nb, padding=10)
            nb.add(f, text=titulo)
            tv = ttk.Treeview(f, columns=(c1, c2), show='headings', height=12)
            tv.heading(c1, text=c1);  tv.column(c1, width=280)
            tv.heading(c2, text=c2);  tv.column(c2, width=100, anchor='center')
            for r in dados:
                tv.insert('', 'end', values=list(r.values()))
            tv.pack(fill='both', expand=True)

        aba("Por Departamento", rel['por_departamento'], "Departamento", "Total")
        aba("Por Status",       rel['por_status'],       "Status",       "Total")
        aba("Por Prioridade",   rel['por_prioridade'],   "Prioridade",   "Total")

        sf = ttk.Frame(nb, padding=28)
        nb.add(sf, text="Resumo Geral")
        resumo = rel['resumo']
        for i, (lbl, val) in enumerate([
            ("Abertos",      resumo['abertos']      or 0),
            ("Em Andamento", resumo['em_andamento'] or 0),
            ("Encerrados",   resumo['encerrados']   or 0),
            ("Cancelados",   resumo['cancelados']   or 0),
        ]):
            ttk.Label(sf, text=lbl, font=('Segoe UI', 12)
                      ).grid(row=i, column=0, sticky='w', pady=10, padx=10)
            ttk.Label(sf, text=str(val), font=('Segoe UI', 14, 'bold')
                      ).grid(row=i, column=1, sticky='e', pady=10, padx=50)

        ttk.Button(top, text='Fechar', command=top.destroy).pack(pady=(0, 10))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def tentar_autoconectar() -> bool:
    """Tenta conectar silenciosamente usando o config.ini salvo."""
    cfg = ler_config()
    if not cfg.get('password'):
        return False
    try:
        DatabaseConnection.get_instance().connect(
            host=cfg['host'],
            database=cfg['database'],
            user=cfg['user'],
            password=cfg['password'],
            port=int(cfg.get('port', 5432))
        )
        return True
    except Exception:
        return False


def main():
    if tentar_autoconectar():
        AppPrincipal()
    else:
        tela = TelaConexao()
        if tela.sucesso:
            tela.janela.destroy()
            AppPrincipal()


if __name__ == '__main__':
    main()
