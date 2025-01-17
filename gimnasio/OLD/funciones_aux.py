from os import path
from colorama import Fore
import json
import pandas as pd
from datetime import date
from urllib.request import urlopen
from requests import get as reqget

HOY = date.today().strftime("%d/%m/%Y")
MES = date.today().strftime("%m/%Y")

#? carpeta actual
dir_path = path.dirname(path.realpath(__file__))

REG_DIARIO_ARCH = path.join(dir_path, 'excels', 'registro_diario.xlsx')
USUARIOS_ARCH = path.join(dir_path, 'excels', 'usuarios.xlsx')
REG_NOM_ARCH = path.join(dir_path, 'excels', 'registro_diario_nombres.xlsx')
REG_DEUDOR_ARCH = path.join(dir_path, 'excels', 'reg_deudor.xlsx')

URL_WITH_API_KEY = 'https://www.googleapis.com/blogger/v3/blogs/1252347762538283834/posts/8185578739401206597/comments?key=AIzaSyAVIUqp3wyqoLQiVYxFrJIFMzGgvvHR7XM'

USUARIOS_TOTAL = [ str(usr) for usr in pd.read_excel(USUARIOS_ARCH)['DNI'].values.tolist() ]

#! a partir de los 15 días se debe el mes entero, sino no se cuenta como que vino ese mes
DIAS_PARA_CONTAR_PRESENCIA = 15

comandos_registro = {
    "ayuda": "obtener más información sobre comandos",
    "descartar": "descarta el último DNI anotado",
    "hoy": "enumera todos los ingresos de clientes del día",
    "quitar X": "quita el cliente en la posición X de los ingresantes del día",
    "comando": "sale del modo registro, entra al modo comando",
    "salir": "guarda la información del registro y cierra el programa"
}

comandos_comando = {
    "ayuda": "obtener más información sobre comandos",
    "cliente": "busca información sobre un cliente particular, se escribe su DNI sin comillas\nsintaxis: cliente 'DNI'",
    "buscliente": "busca un nombre entre todos los clientes y devuelve una lista de coincidencias\nsintaxis: buscliente 'nombre'",
    "nombresreg": "lee todo el registro histórico para traducir los DNI's a nombres y lo guarda en archivo",
    "nuevoCliente": "abre un formulario para añadir un nuevo cliente",
    "presencia": "devuelve los ultimos dias en los que vino un cliente (DNI), si el numero es 0 devuelve todos\nsintaxis: presencia 'numero dias' 'DNI'",
    "deudores": "enumera clientes deudores en orden descendiente por meses adeudados",
    "totalMes": "devuelve la ganancia total de un mes particular\nsintaxis: totalMes 'MM/AAAA'",
    "registro": "sale del modo comando, vuelve al modo registro",
    "adeudado": "devuelve la cantidad de meses adeudados de un cliente particular\nsintaxis: adeudado 'DNI'",
    "pagar": "paga un mes de cuota, el segundo argumento es opcional, si no se pone paga el mes actual, pero si se pone paga ese mes particular para ese cliente\nsintaxis: pagar 'DNI' 'MM/AAAA'",
    "salir": "guarda la información del registro y cierra el programa"
}


#region [black] #? funciones de comando

def guardar_registro_diario(ingresados):
    dnis = ' '.join(ingresados)

    print(Fore.YELLOW + 'guardando registro...')
    print('ingresados hoy:', dnis)
    print(Fore.RESET)

    df_guardar_reg = pd.read_excel(REG_DIARIO_ARCH).set_index('fecha')

    if HOY not in df_guardar_reg.index:
        df_guardar_reg.loc[HOY, 'dnis'] = dnis
    else:
        dni_ya_ingresados = str(df_guardar_reg.loc[HOY, 'dnis']).split()

        if dni_ya_ingresados == ['nan']: dni_ya_ingresados = []

        todos_dnis = ' '.join(list(set(ingresados + dni_ya_ingresados))) 
        if todos_dnis == 'nan':
            todos_dnis = ''
        df_guardar_reg.loc[HOY, 'dnis'] = todos_dnis       
    
    try:
        df_guardar_reg.to_excel(REG_DIARIO_ARCH)
    except:
        print(Fore.RED + 'por favor cierre el archivo registro_diario.xlsx para poder guardar los cambios')
        input('presione enter para volver a intentar guardar')
        print(Fore.RESET)
        guardar_registro_diario(ingresados)

def crear_reg_con_nombres():
    'actualiza el archivo "registro_diario_nombres.excel" para pasar el registro en formato DNIs a nombres'

    usuarios_df = pd.read_excel(USUARIOS_ARCH).set_index('DNI')
    registro_df = pd.read_excel(REG_DIARIO_ARCH)
    registro_nombres_df = pd.DataFrame(columns=["fecha", "dnis"])

    # itera por cada fila en el registro histórico
    # y traduce los DNI's en el registro a nombres
    # para después pasar esa dataframe al archivo reg_nombres.excel
    for index, row in registro_df.iterrows():
        lista_nombres = []
        fecha = row['fecha']
        try:
            dnis = str(row['dnis']).split()
            for dni in dnis:
                dni = int(dni)
                lista_nombres.append( usuarios_df.loc[dni, 'nombre'] )
        except:
            dnis = str(row['dnis'])
            if dnis == 'nan':
                continue
            lista_nombres.append(usuarios_df.loc[dnis, 'nombre'])

        registro_nombres_df.loc[index, 'fecha'] = fecha
        registro_nombres_df.loc[index, 'dnis'] = ' - '.join(lista_nombres)

    # intenta guardar el archivo, si está abierto en alguna otra aplicación lo avisa y vuele a intentarlo
    try:
        registro_nombres_df = registro_nombres_df.set_index('fecha')
        registro_nombres_df.to_excel(REG_NOM_ARCH)
    except:
        print(Fore.RED + 'por favor cierre el archivo registro_nombres.xlsx para poder guardar los cambios')
        print(Fore.RESET)
        input('presione enter para volver a intentar')
        crear_reg_con_nombres()
    
def buscar_cliente(dni:str) -> list:
    'dado un dni devuelve una lista con la información del usuario encontrado'
    # [(columna, info)]

    df_usuarios = pd.read_excel(USUARIOS_ARCH).set_index('DNI')

    for index_dni, row in df_usuarios.iterrows():
        if str(index_dni) == dni:
            return list(zip( df_usuarios.columns, row.tolist() ))

    return None

def buscar_cliente_nombre(nombre:str) -> list:
    'busca un cliente por nombre y devuelve una serie de coincidencias con la búsqueda'
    resultados = []

    df_usuarios = pd.read_excel(USUARIOS_ARCH)
    resultados.append(df_usuarios.columns)
    for index, row in df_usuarios.iterrows():
        if nombre.lower() in row['nombre'].lower():
            resultados.append(row.tolist())

    return resultados

def presencia(ultimos_n_dias:str, dni:str) -> list:
    'dado un número n de días y un dni devuelve los últimos n días en los que ese cliente ingresó al gimnasio en el formato ["DD"/"MM"/"AAAA"]'
    dias_cont_venidos = 0
    dias_venidos = []
    ultimos_n_dias = int(ultimos_n_dias)

    df_reg = pd.read_excel(REG_DIARIO_ARCH)
    #! tiene el problema que itera al revés, empezando por los días más viejos hacia los más nuevos
    #! de manera que no devuelve el último día, sino el primero
    for index, row in df_reg.iterrows():
        if dias_cont_venidos == ultimos_n_dias: return dias_venidos

        # me da una lista de DNIs, puede tener un único dni
        lista_dnis = str(row['dnis']).split()

        if dni in lista_dnis:
            dias_venidos.append(row['fecha'])
            dias_cont_venidos += 1
        

    return dias_venidos

def ordenar_usuarios():
    'ordena los usuarios alfabéticamente'

    df_usuarios = pd.read_excel(USUARIOS_ARCH).set_index('DNI')

    # ordena todas las filas de usuarios por nombre
    df_usuarios = df_usuarios.sort_values(by=['nombre'])

    try:
        df_usuarios.to_excel(USUARIOS_ARCH)
    except:
        print(Fore.RED + 'por favor cierre el archivo usuarios.xlsx para poder guardar los cambios')
        input('presione enter para volver a intentar guardar')
        print(Fore.RESET)
        ordenar_usuarios()

def meses_adeudados(dni_usr:str) -> list:
    'asumiendo que los DNIs en el archivo son DNIs reales, devuelve una lista de los meses en los que esa persona vino y no pagó'
    lista_meses_adeudados = []

    df_reg_deudas = pd.read_excel(REG_DEUDOR_ARCH).set_index('mes')
    # mes       |   vinieron    |   pagaron
    # 08/2023       zodaka,juan     zodaka
    
    # en vez de tener nombres en el archivo tendremos DNI's
    for mes, row in df_reg_deudas.iterrows():
        vinieron_ese_mes = str(row['vinieron']).split()
        pagaron_ese_mes = str(row['pagaron']).split()

        if dni_usr in vinieron_ese_mes and dni_usr not in pagaron_ese_mes:
            lista_meses_adeudados.append(mes)

    return lista_meses_adeudados

def pagar_mes(dni_usr:str, mes:str = MES) -> None:
    'paga la cuota mensual de un cliente, si se especifica el mes se puede pagar a pasado y futuro, sino se toma el mes actual'
    if dni_usr not in USUARIOS_TOTAL:
        print(Fore.RED + 'el dni no pertenece a la base de datos de usuarios')
        print(Fore.RESET)
        return None
    
    df_reg_deudas = pd.read_excel(REG_DEUDOR_ARCH).set_index('mes')
    
    # mes       |   vinieron    |   pagaron
    # 08/2023       zodaka,juan     zodaka
    
    if mes not in df_reg_deudas.index:
        df_reg_deudas.loc[mes, 'pagaron'] = dni_usr
    else:
        # ya hay gente anotada para ese mes
        try:
            # hay una sola persona
            pagados = str(int(df_reg_deudas.loc[mes, 'pagaron'])).split()
        except:
            # hay más de una
            pagados = str(df_reg_deudas.loc[mes, 'pagaron']).split()
        
        if pagados == ['nan']:
            pagados = []

        if dni_usr in pagados:
            print(Fore.YELLOW + 'el cliente ya pagó el mes')
            print(Fore.RESET)
        else:
            pagados.append(dni_usr)

        df_reg_deudas.loc[mes, 'pagaron'] = ' '.join(pagados)

    try:
        df_reg_deudas.to_excel(REG_DEUDOR_ARCH)
    except:
        print(Fore.RED + 'por favor cierre el archivo reg_deudor.xlsx para poder guardar los cambios')
        input('presione enter para volver a intentar guardar')
        print(Fore.RESET)
        pagar_mes(dni_usr, mes)

def deudores() -> list:
    'devuelve una lista de tuplas ordenada de la forma (meses_adeudados:str, DNI:str)'
    lista_deudores_ord = []

    for usr in USUARIOS_TOTAL:
        meses = len(meses_adeudados(usr))
        if meses > 0:
            lista_deudores_ord.append( (str(meses), usr) )
    
    lista_deudores_ord.sort(reverse=True)

    return lista_deudores_ord

def actualizar_reg_deudor():
    'a partir de la lectura del archivo de registro diario anota en el registro actualiza el reg_deudor para poner aquellos clientes que hayan ingresado al gym hasta entonces'
    #! a partir de los 15 días se debe el mes entero, sino no se cuenta como que vino ese mes
    # [ ( mes, [dni] ) ]
    ingr_por_mes = {}
    lista_meses = []
    reg_total_cont = []
    df_reg_hist = pd.read_excel(REG_DIARIO_ARCH).set_index('fecha')

    # obtengo una lista de meses con sus respectivos ingresantes por cada mes
    # los ingresantes se repiten la cantidad de veces que 
    for fecha, row in df_reg_hist.iterrows():
        mes:str = fecha[3:] # type: ignore
        dnis:list = str(row['dnis']).split()
        
        if mes in ingr_por_mes.keys():
            ingr_por_mes[mes] = ingr_por_mes[mes]+dnis
        else:
            ingr_por_mes[mes] = dnis
            lista_meses.append(mes)

    # cuenta la cant de veces que aparece una persona por mes en el gimnasio
    for mes, ingresantes in ingr_por_mes.items():
        cont = {} # dni: cant entradas:int
        for persona in ingresantes:
            if persona in cont.keys():
                cont[persona] += 1
            else:
                cont[persona] = 1
        
        reg_total_cont.append(cont)

    # ahora devuelvo una lista de diccionarios en donde cada dict es un mes
    # y cada key es un DNI, cada valor un bool
    # true si vino al gim, false sino
    for mes in reg_total_cont:
        for dni, presencialidad in mes.items():
            mes[dni] = presencialidad >= DIAS_PARA_CONTAR_PRESENCIA
    
    reg_total_cont = list(zip(lista_meses, reg_total_cont))

    df_reg_deudor = pd.read_excel(REG_DEUDOR_ARCH).set_index('mes')

    # anota en cada casilla todos los que vinieron por cada mes
    for mes, usuarios in reg_total_cont:
        anotados_vinieron_ese_mes = []
        # el mes no fue anotado todavía, anoto todos los que entraron ese mes
        for dni, vino in usuarios.items():
            # dni:str, vino:bool
            if vino: anotados_vinieron_ese_mes.append(dni)

        df_reg_deudor.loc[mes, 'vinieron'] = ' '.join(list(set(anotados_vinieron_ese_mes)))

    print(Fore.BLUE + 'procediendo a guardar los datos cargados al sistema de deudores...')
    print(Fore.RESET)
    try:
        df_reg_deudor.to_excel(REG_DEUDOR_ARCH)
    except:
        print(Fore.YELLOW + 'por favor cierre el archivo reg_deudores.xlsx para poder guardar los datos')
        input('presione enter para volver a intentar')
        print(Fore.RESET)
        actualizar_reg_deudor()

def total_mes(mes:str) -> int:
    dnis_que_pagaron = []

    df_reg_deudas = pd.read_excel(REG_DEUDOR_ARCH).set_index('mes')

    try:
        # en caso de que sea una única persona que pagó
        dnis_que_pagaron = str(int(df_reg_deudas.loc[mes,'pagaron'])).split()
    except:
        dnis_que_pagaron = str(df_reg_deudas.loc[mes,'pagaron']).split()
    
    if dnis_que_pagaron == ['nan']:
        dnis_que_pagaron = []

    return len(dnis_que_pagaron)

#endregion


#region [purple] #! funciones de check de pago

def dir_ip():
    'obtiene la ip desde donde se ejecuta el programa'
    url = 'https://api.ipify.org'
    try:
        response = reqget(url)
    except:
        print(Fore.YELLOW + 'conéctese a internet!')
        print(Fore.RESET)
        return None
    ip_address = response.text
    return ip_address

def check() -> bool:
    '🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊'

    computer_ip = dir_ip()
    if computer_ip == None:
        print(Fore.YELLOW + 'error conexión: por favor conéctese a internet para mantener actualizados los paquetes')
        print(Fore.RESET)
        return False

    #? comandos en los comentarios de blogger
    #* newip 0.0.0.0 
    # añade una nueva ip a la lista de ip's permitidas
    #* delip 0.0.0.0
    # borra una ip de la lista de ip's permitidas

    checked:bool = False
    ip_s = set()

    source = urlopen(URL_WITH_API_KEY).read()
    data = json.loads(source)

    for item in data["items"]:
        usuario, comentario = item['author']['displayName'], item['content']
        
        # chequeo que el comment sea mio masvale B))))))
        if usuario != 'zodak': continue

        comando, ip = comentario.split()

        # sección comandos
        if comando == 'newip':
            ip_s.add(ip)
        elif comando == 'delip':
            ip_s.discard(ip)

    checked = ip_s.__contains__(computer_ip)

    return checked

#endregion
