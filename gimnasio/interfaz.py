import ttkbootstrap as ttk
from ttkbootstrap.scrolled import ScrolledFrame
from ttkbootstrap.tableview import Tableview
from funciones_aux import *
from tkinter import messagebox

#// todo: PARA AÑADIR NUEVO USUARIO ABRIR UNA VENTANA EXTRA PARA LLENAR EL FORMULARIO, mirar formulario.py
    #// ? hacerlo para cada comando, personalizado, y que esté integrado en la columna central
    #// (que no se abra una ventana aparte)
#// todo: hacer un ScrolledFrame para el label que explica que hace cada comando
#// todo: hacer otro scrolledFrame para el label que muestra el resultado de cada comando ejecutado  
#// todo: botón guardar debe guardar la información del día de hoy
#// todo: que no se pueda cerrar la ventana antes de guardar los datos
#// todo: usar calendar para buscar por meses
# todo: poner un toggleButton para cambiar entre modo oscuro y claro
# todo: poder abrir los excels de la base de datos desde el programa
# todo: agregar número de emergencia
#// todo: en DEUDORES hacer que aparezcan nombres, dnis y meses adeudados en un estilo TABLA
#// todo: pasar todos los botones a bootstrap
#// todo: hacer que deudores aparezca en forma de tabla
#// todo: hacer tabla para el comando presencia
#// todo: terminar de hacer el comando TOTALMES
#// todo: terminar de hacer el comando ADEUDADO
#// todo: terminar de hacer el comando PAGAR

modo_registro = True    
BP = 30                 # button padding (lo uso en muchos paddings)
TLF = 15                # tamaño letra formulario

app = ttk.Window(themename="litera")
app.title("Administración Gimnasio  🦾")
# hago que sea pantalla completa
width= app.winfo_screenwidth()               
height= app.winfo_screenheight()               
app.geometry(f"{width}x{height}")

lista_de_ingresados_hoy = []
info_guardada = False

#region [purple] #? FUNCIONES QUE CAMBIAN GUI

def cambiar_modo() -> None:
    global modo_registro
    if modo_registro == True:
        modo_registro = False
        ocultar_wid_registro()
        mostrar_wid_comando()
    else:
        modo_registro = True
        ocultar_wid_comando()
        mostrar_wid_registro()

def obtener_valores_hijos(frame: ttk.Frame) -> list:
    """
    devuelve un dict con los valores de todos los hijos de un frame, también hace recursión en cada Frame que tenga dentro
    arranca a nombrar las variables desde start_index
    """
    valores_formulario = []

    for child in frame.winfo_children():
        # si el widget no se puede ver, no quiero información de ese widget
        if not child.winfo_viewable(): continue

        widget_type = type(child).__name__

        if widget_type == 'Entry':
            valores_formulario.append(child.get())
        elif widget_type == 'Combobox':
            valores_formulario.append(child.get())
        elif widget_type == 'Checkbutton':
            valores_formulario.append(child.instate(['selected']))
        elif widget_type == 'DateEntry':
            valores_formulario.append(child.entry.get())
        elif widget_type == 'Frame':
            valores_formulario += obtener_valores_hijos(child)
    
    return valores_formulario

def recargar_tabla(tabla: Tableview, respuesta:list) -> None:
    "vacía la tabla -scroll_res_comando- y pone las filas -respuesta-"

    scroll_res_comando.pack_forget()
    tabla.pack(fill="both", expand=True)
    tabla.delete_rows()
    tabla.insert_rows(index='end', rowdata=respuesta)
    tabla.load_table_data()

def enviar_formulario() -> None:
    """
    ejecuta el comando seleccionado de la comboBox usando los valores del formulario para ello
    """
    comando_seleccionado_para_enviar = selecc_comandos.get()
    valores_formulario = obtener_valores_hijos(scroll_formulario)    # busco todos los datos de scroll_formulario
    res = globals()[comando_seleccionado_para_enviar](*valores_formulario)

    if comando_seleccionado_para_enviar == 'deudores':
        recargar_tabla(tabla_deudores, res)
    elif comando_seleccionado_para_enviar == 'busCliente':
        recargar_tabla(tabla_buscliente, res)
    else:
        tabla_deudores.pack_forget()
        tabla_buscliente.pack_forget()
        scroll_res_comando.pack(expand=True, fill="both")
        resultado_comando.pack(expand=True, fill="both", padx=10, pady=10)
        resultado_comando['text'] = res

def actualizar_comando(_) -> None:
    "refresca la información útil sobre cada comando que se vaya eligiendo"
    elegido = selecc_comandos.get()
    ayuda_comando.config(text = comandos_comando[elegido])
    quitar_formulario()
    globals()[elegido+'_GUI']()

def contrast_color() -> str:
    '''detecta si el tema es oscuro o claro y devuelve un string con un color opuesto al tema para hacer contraste con el fondo'''
    if app.style.theme.type == 'dark':
        return 'light'
    else:
        return 'dark'

#endregion

#region [red] #? funciones de REGISTRO

def ingresar() -> None:
    "ingresa un DNI en el modo registro y devuelve un mensaje de resultado"
    dni_usr = dni_input.get()

    if dni_usr in lista_de_ingresados_hoy:
        res_ingreso_dni['text'] = "Este DNI ya está en la lista de ingresados de hoy."
    elif dni_usr in USUARIOS_TOTAL:
        lista_de_ingresados_hoy.append(dni_usr)
        res_ingreso_dni['text'] = "Ingresado con éxito!"
        tabla_ingresados_hoy.insert_row(index='end', values=[dni_usr, NOMBRES_POR_DNI[dni_usr]])
        tabla_ingresados_hoy.load_table_data()
    else:
        res_ingreso_dni['text'] = "Este DNI no pertenece a la base de usuarios."
    
def guardar_dia() -> None:
    global info_guardada
    try:
        res_ingreso_dni['text'] = "Guardando ingresos..."
        guardar_registro_diario(lista_de_ingresados_hoy)
        res_ingreso_dni['text'] = "Guardado con éxito."
        info_guardada = True
    except PermissionError as err:
        res_ingreso_dni['text'] = err

def quitar_registro_persona() -> str:
    "quita una persona del registro de los ingresados en el día de hoy"
    for row in tabla_ingresados_hoy.get_rows(selected=True):
        lista_de_ingresados_hoy.remove(row.values[0])

    tabla_ingresados_hoy.delete_rows(iids=tabla_ingresados_hoy.view.selection())

def al_cerrar() -> None:
    global info_guardada
    if not info_guardada:
        if messagebox.askokcancel("Información sin guardar", "Hay información sin guardar, ¿está seguro de querer cerrar?"):
            app.destroy()
    else:
        app.destroy()

#endregion


#region [purple] #? estilos
estilo = ttk.Style()
estilo.configure('TButton', font=('Gill Sans MT', 20))
estilo.configure('tituloAPP.Label', font=('Gill Sans MT', 30))
#endregion

#* clases útiles
class WrappingLabel(ttk.Label):
    '''a type of Label that automatically adjusts the wrap to the size'''
    def __init__(self, master=None, **kwargs):
        ttk.Label.__init__(self, master, **kwargs)
        self.bind('<Configure>', lambda e: self.config(wraplength=self.winfo_width()))

#region [black] #* widgets MODO REGISTRO
title = ttk.Label(app, text="Administrador De Gimnasios", style="tituloAPP.Label")

input_label =   ttk.Label(app, text="Ingrese DNI", font=('Gill Sans MT', 20))

barra_busqueda_ingreso = ttk.Frame(app)
dni_input = ttk.Entry(barra_busqueda_ingreso, font=('Gill Sans MT', 20))
ingresar_dni = ttk.Button(barra_busqueda_ingreso, text="✅", command=ingresar)

cuadro_res_ingreso_dni = ttk.Labelframe(app, text='Resultado del ingreso del DNI correspondiente', bootstyle=contrast_color())
res_ingreso_dni = WrappingLabel(cuadro_res_ingreso_dni, justify='left', font=('Gill Sans MT', 15), bootstyle='warning')

tabla_ingresados_hoy = Tableview(app, bootstyle="dark", coldata=["DNI", "Nombre"])

modo =      ttk.Button(text="MODO", bootstyle='dark', command=cambiar_modo)
quitar =    ttk.Button(text="QUITAR", bootstyle='danger', command=quitar_registro_persona)
guardar =   ttk.Button(text="GUARDAR", bootstyle='success', command= guardar_dia)
#endregion

#region [black] #* widgets MODO COMANDO
barra_selec_comando = ttk.Frame(app)
selecc_comandos = ttk.Combobox(
    barra_selec_comando,
    state="readonly",
    values= list(comandos_comando),
    font=('Gill Sans MT', 25),
    bootstyle=contrast_color()
)

selecc_comandos.bind('<<ComboboxSelected>>', actualizar_comando)

cuadro_formulario = ttk.Labelframe(app, text='Formulario', bootstyle=contrast_color())
scroll_formulario = ScrolledFrame(cuadro_formulario)

enviar_formulario_frame = ttk.Button(app, text='Enviar', bootstyle=f'{contrast_color()}-outline', command=enviar_formulario)

cuadro_resultado_comando = ttk.LabelFrame(app, text='Resultado del comando ejecutado', bootstyle='info')
scroll_res_comando = ScrolledFrame(cuadro_resultado_comando)
resultado_comando = WrappingLabel(scroll_res_comando, justify='left', font=('Gill Sans MT', 15))

cuadro_ayuda_comando = ttk.Labelframe(app, text='Más información sobre comandos', bootstyle='info')
scroll_ayuda_comando = ScrolledFrame(cuadro_ayuda_comando)
ayuda_comando = WrappingLabel(scroll_ayuda_comando, justify='left', font=('Gill Sans MT', 15))

#endregion

#region [black] #? widgets FORMULARIOS
#! CLIENTE
# recibe dni
label_cliente_dni = ttk.Label(scroll_formulario, text='DNI', font=('Gill Sans MT', TLF))
input_cliente_dni = ttk.Entry(scroll_formulario, font=('Gill Sans MT', TLF))

#! BUSCLIENTE  
label_buscliente = ttk.Label(scroll_formulario, text='Nombre', font=('Gill Sans MT', TLF))
input_buscliente = ttk.Entry(scroll_formulario, font=('Gill Sans MT', TLF))
tabla_buscliente = Tableview(cuadro_resultado_comando, searchable=True, bootstyle="dark", coldata=["DNI", "Nombre", "Teléfono", "Domicilio", "Anotaciones"])

#! NUEVOCLIENTE
grid_descartable = ttk.Frame(scroll_formulario)
label_1_nuevocliente = ttk.Label(grid_descartable, text='Nombre y Apellido', font=('Gill Sans MT', TLF))
input_1_nuevocliente = ttk.Entry(grid_descartable, font=('Gill Sans MT', TLF))

label_2_nuevocliente = ttk.Label(grid_descartable, text='DNI', font=('Gill Sans MT', TLF))
input_2_nuevocliente = ttk.Entry(grid_descartable, font=('Gill Sans MT', TLF))

label_3_nuevocliente = ttk.Label(grid_descartable, text='Teléfono', font=('Gill Sans MT', TLF))
input_3_nuevocliente = ttk.Entry(grid_descartable, font=('Gill Sans MT', TLF))

label_4_nuevocliente = ttk.Label(grid_descartable, text='Dirección', font=('Gill Sans MT', TLF))
input_4_nuevocliente = ttk.Entry(grid_descartable, font=('Gill Sans MT', TLF))

label_5_nuevocliente = ttk.Label(grid_descartable, text='Anotaciones', font=('Gill Sans MT', TLF))
input_5_nuevocliente = ttk.Entry(grid_descartable, font=('Gill Sans MT', TLF))

#! PRESENCIA
grid_descartable_2 = ttk.Frame(scroll_formulario)
label_1_presencia = ttk.Label(grid_descartable_2, text='Número de Días', font=('Gill Sans MT', TLF))
input_1_presencia = ttk.Entry(grid_descartable_2, font=('Gill Sans MT', TLF))

label_2_presencia = ttk.Label(grid_descartable_2, text='DNI', font=('Gill Sans MT', TLF))
input_2_presencia = ttk.Entry(grid_descartable_2, font=('Gill Sans MT', TLF))

#! TOTALMES
label_1_totalmes = ttk.Label(scroll_formulario, text='Mes y Año', font=('Gill Sans MT', TLF))
entrada_anio_fecha_totalmes = ttk.DateEntry(scroll_formulario, dateformat=r'%m/%Y')

#! ADEUDADO
label_adeudado = ttk.Label(scroll_formulario, text='DNI', font=('Gill Sans MT', TLF))
input_adeudado = ttk.Entry(scroll_formulario, font=('Gill Sans MT', TLF))
tabla_deudores = Tableview(cuadro_resultado_comando, searchable=True, bootstyle="dark", coldata=["DNI", "Nombre", "Num. meses adeudados"])

#! PAGAR
grid_descartable_3 = ttk.Frame(scroll_formulario)
label_1_pagar = ttk.Label(grid_descartable_3, text='DNI', font=('Gill Sans MT', TLF))
label_2_pagar = ttk.Label(grid_descartable_3, text='Mes y Año', font=('Gill Sans MT', TLF))
entrada_mes_pagar = ttk.DateEntry(grid_descartable_3, dateformat=r'%m/%Y')
input_pagar = ttk.Entry(grid_descartable_3, font=('Gill Sans MT', TLF))
#endregion

#region [black] #* creo filas y columnas
app.columnconfigure(0, weight=1, uniform="a")
app.columnconfigure((1,2), weight=2, uniform="a")

app.rowconfigure((0,1,2,4,5), weight=1, uniform="a")
app.rowconfigure(3, weight=2, uniform="a")
#endregion

#? funciones de cambio de MODO ------------------------------------------------------------------------------------

def mostrar_wid_registro():
    title.grid(row=0, column=0, sticky="nsw", padx=50, pady=15, columnspan=2)
    input_label.grid(row=1, column=2, sticky="sw", padx=30)

    ingresar_dni.pack(side="right", fill="both")
    dni_input.pack(side="right", fill="both", expand=True)
    barra_busqueda_ingreso.grid(row=2, column=2, sticky="nwe", padx=BP, pady=BP)

    cuadro_res_ingreso_dni.grid(row=3, column=2, sticky="nwe", padx=BP)
    res_ingreso_dni.pack(expand=True, fill="both", padx=10, pady=10)

    tabla_ingresados_hoy.grid(column=1, row=2, rowspan=4, sticky="nswe", padx=BP, pady=BP)

    modo.grid(row=2, column=0, sticky="nswe", padx=BP, pady=BP)
    quitar.grid(row=4, column=0, sticky="nswe", padx=BP, pady=BP)
    guardar.grid(row=5, column=0, sticky="nswe", padx=BP, pady=BP)

def ocultar_wid_registro():
    input_label.grid_remove()
    barra_busqueda_ingreso.grid_remove()
    tabla_ingresados_hoy.grid_remove()
    cuadro_res_ingreso_dni.grid_remove()
    quitar.grid_remove()

def mostrar_wid_comando():
    barra_selec_comando.grid(row=1, column=0, sticky="we", padx=BP, pady=BP)
    selecc_comandos.pack(side="left", fill="both", expand=True)

    cuadro_formulario.grid(row=1, column=1, rowspan=4, sticky="nswe", padx=BP, pady=BP)
    scroll_formulario.pack(expand=True, fill="both")

    enviar_formulario_frame.grid(row=5, column=1, sticky="nswe", padx=BP, pady=BP)

    cuadro_resultado_comando.grid(row=1, column=2, rowspan=5, sticky="nsew", padx=BP, pady=BP)
    
    cuadro_ayuda_comando.grid(row=3, column=0, sticky="nsew", padx=BP, pady=BP, rowspan=2)
    scroll_ayuda_comando.pack(expand=True, fill="both")
    ayuda_comando.pack(expand=True, fill="both", padx=10, pady=10)

def ocultar_wid_comando():
    selecc_comandos.grid_remove()
    cuadro_resultado_comando.grid_remove()
    cuadro_formulario.grid_remove()
    barra_selec_comando.grid_remove()
    enviar_formulario_frame.grid_remove()
    cuadro_ayuda_comando.grid_remove()

#? funciones de formulario
def cliente_GUI():
    label_cliente_dni.pack(side='left', padx=BP)
    input_cliente_dni.pack(side='left', padx=BP, fill='x', expand=True)
def busCliente_GUI():
    label_buscliente.pack(side='left', padx=BP)
    input_buscliente.pack(side='left', padx=BP, fill='x', expand=True)
def nombresReg_GUI():
    pass
def nuevoCliente_GUI():
    grid_descartable.columnconfigure(0, uniform='a', pad=10)
    grid_descartable.columnconfigure(1, weight=2, uniform='a', pad=10)
    grid_descartable.rowconfigure((0,1,2,3,4), pad=10, uniform='a')

    grid_descartable.pack(expand=True, fill="both")

    label_1_nuevocliente.grid(column=0, row=0)
    input_1_nuevocliente.grid(column=1, row=0, sticky="we", padx=20)

    label_2_nuevocliente.grid(column=0, row=1)
    input_2_nuevocliente.grid(column=1, row=1, sticky="we", padx=20)

    label_3_nuevocliente.grid(column=0, row=2)
    input_3_nuevocliente.grid(column=1, row=2, sticky="we", padx=20)
    
    label_4_nuevocliente.grid(column=0, row=3)
    input_4_nuevocliente.grid(column=1, row=3, sticky="we", padx=20)

    label_5_nuevocliente.grid(column=0, row=4)
    input_5_nuevocliente.grid(column=1, row=4, sticky="we", padx=20)
def presencia_GUI():
    grid_descartable_2.columnconfigure(0, uniform='a', pad=10)
    grid_descartable_2.columnconfigure(1, weight=2, uniform='a', pad=10)
    grid_descartable_2.rowconfigure((0,1), pad=10, uniform='a') 

    grid_descartable_2.pack(expand=True, fill="both")

    label_1_presencia.grid(column=0, row=0)
    input_1_presencia.grid(column=1, row=0, sticky="we", padx=20)

    label_2_presencia.grid(column=0, row=1)
    input_2_presencia.grid(column=1, row=1, sticky="we", padx=20)
def deudores_GUI():
    pass
def totalMes_GUI():
    label_1_totalmes.pack(side='left', expand=True)
    entrada_anio_fecha_totalmes.pack(side='left', padx=BP)
def adeudado_GUI():
    label_adeudado.pack(side='left', padx=BP)
    input_adeudado.pack(side='left', padx=BP, fill='x', expand=True)
def pagar_GUI():
    grid_descartable_3.columnconfigure(0, uniform='a', pad=10)
    grid_descartable_3.columnconfigure(1, weight=2, uniform='a', pad=10)
    grid_descartable_3.rowconfigure((0,1), pad=10, uniform='a') 
    grid_descartable_3.pack(expand=True, fill="both")

    label_1_pagar.grid(column=0, row=0)
    input_pagar.grid(column=1, row=0, sticky="we", padx=20)
    label_2_pagar.grid(column=0, row=1)
    entrada_mes_pagar.grid(column=1, row=1)

def quitar_formulario():
    '''elimina el anterior formulario dejando el widget vacío'''
    for widget in scroll_formulario.winfo_children():
        widget.pack_forget()

#!--------------------------------------------------------------------------------------------------------------------
#! INICIA PROGRAMA

app.protocol("WM_DELETE_WINDOW", al_cerrar)
mostrar_wid_registro()
app.mainloop()