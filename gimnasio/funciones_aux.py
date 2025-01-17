from os import path
import pandas as pd
from datetime import date
import json
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

def generar_dict_dni_a_nombre() -> dict:
    dict = {}
    df_usuarios = pd.read_excel(USUARIOS_ARCH, dtype=str, keep_default_na=False).set_index('DNI')

    for dni, row in df_usuarios.iterrows():
        dict[dni] = row['nombre']

    return dict

NOMBRES_POR_DNI = generar_dict_dni_a_nombre()

USUARIOS_TOTAL = [ str(usr) for usr in pd.read_excel(USUARIOS_ARCH)['DNI'].values.tolist() ]

# número de días necesarios para contar que un cliente vino tal mes
DIAS_PARA_CONTAR_PRESENCIA = 1

comandos_comando = {
    "cliente": "Busca información en la base de usuarios sobre un cliente particular.",
    "busCliente": "Busca un nombre entre todos los clientes y devuelve una lista de coincidencias.",
    "nombresReg": "Lee el registro histórico para traducir los DNI's a nombres y lo guarda en el archivo registro_diario_nombres.xlsx.",
    "nuevoCliente": "Abre un formulario para añadir un nuevo cliente.",
    "presencia": "Devuelve los ultimos dias en los que vino un cliente, si no se da un número de días devuelve todos los días que vino.",
    "deudores": "Enumera todos los clientes deudores por meses adeudados.",
    "totalMes": "Devuelve la cantidad de clientes que pagaron un mes particular.",
    "adeudado": "Devuelve los meses adeudados de un cliente.",
    "pagar": "Paga un mes de cuota de un cliente, si no se elige un mes se toma el actual."
}

#!------------------------------------------------ LISTA DE COSAS POR ARREGLAR
# TODO: optimizar todas las funciones para no tener que hacer loops, más info sobre esto en:
    # https://realpython.com/fast-flexible-pandas/
    # https://towardsdatascience.com/efficiently-iterating-over-rows-in-a-pandas-dataframe-7dd5f9992c01

# TODO: [NO IMPORTANTE] reemplazar todos los iterrows por itertuples
#!------------------------------------------------

#region [black] #? funciones de COMANDO

#! ya optimizada
def guardar_registro_diario(ingresados:list) -> None:
    if len(ingresados) == 0:
        return None

    df_guardar_reg = pd.read_excel(REG_DIARIO_ARCH, dtype=str, keep_default_na=False).set_index('fecha')

    if HOY not in df_guardar_reg.index:
        dnis = ' '.join(ingresados)
        df_guardar_reg.loc[HOY, 'dnis'] = dnis
    else:
        dni_ya_ingresados = set(df_guardar_reg.loc[HOY, 'dnis'].split())
        
        dni_ya_ingresados.update( set(ingresados) )

        todos_dnis = ' '.join(dni_ya_ingresados) 

        df_guardar_reg.loc[HOY, 'dnis'] = todos_dnis       
    
    try:
        df_guardar_reg.to_excel(REG_DIARIO_ARCH)
    except:
        raise PermissionError('Por favor cierre el archivo registro_diario.xlsx para poder guardar los cambios.')

def nombresReg() -> str:
    """actualiza el archivo "registro_diario_nombres.excel" para pasar el registro en formato DNIs a nombres
    la función lee -todo- el archivo, eso podría mejorarse para que sólo leyera el último día"""

    registro_df = pd.read_excel(REG_DIARIO_ARCH, dtype=str, keep_default_na=False)
    registro_nombres_df = pd.DataFrame(columns=["fecha", "dnis"])

    # itera por cada fila en el registro histórico
    # y traduce los DNI's en el registro a nombres
    # para después pasar esa dataframe al archivo reg_nombres.excel
    for index, row in registro_df.iterrows():
        lista_nombres = []
        fecha = row['fecha']

        dnis = row['dnis'].split()
        for dni in dnis: lista_nombres.append( NOMBRES_POR_DNI[dni] )

        registro_nombres_df.loc[index, 'fecha'] = fecha
        registro_nombres_df.loc[index, 'dnis'] = ' - '.join(lista_nombres)

    # intenta guardar el archivo, si está abierto en alguna otra aplicación lo avisa y vuele a intentarlo
    try:
        registro_nombres_df.set_index('fecha').to_excel(REG_NOM_ARCH)
        return "Actualizado el registro de nombres en registro_diario_nombres.xlsx con éxito."
    except:
        return "por favor cierre el archivo registro_diario_nombres.xlsx para poder guardar los cambios"
    
def buscar_cliente(dni:str) -> (list | None):
    'dado un dni devuelve una lista con la información del usuario encontrado'
    # [(columna, info)]

    df_usuarios = pd.read_excel(USUARIOS_ARCH, dtype=str, keep_default_na=False).set_index('DNI')

    for index_dni, row in df_usuarios.iterrows():
        if index_dni == dni:
            return list(zip( df_usuarios.columns, row.tolist()))

    return None

def busCliente(nombre:str) -> list:
    'busca un cliente por nombre y devuelve una serie de coincidencias con la búsqueda'
    resultados = []

    df_usuarios = pd.read_excel(USUARIOS_ARCH, dtype=str, keep_default_na=False)

    for _, row in df_usuarios.iterrows():
        if nombre.lower() in row['nombre'].lower():
            resultados.append(row.tolist())
    
    return resultados

def presencia(ultimos_n_dias:str, dni:str) -> str:
    'dado un número n de días y un dni devuelve los últimos n días en los que ese cliente ingresó al gimnasio en el formato ["DD"/"MM"/"AAAA"]'
    dias_cont_venidos = 0
    dias_venidos = []
    
    if ultimos_n_dias == '':
        ultimos_n_dias = -1
    else:
        ultimos_n_dias = int(ultimos_n_dias)

    df_reg = pd.read_excel(REG_DIARIO_ARCH, dtype=str, keep_default_na=False)

    for row in reversed(list(df_reg.itertuples())):
        if dias_cont_venidos == ultimos_n_dias: 
            break

        # reviso si el dni está entre los que vinieron aquél día
        lista_dnis = row.dnis.split()

        if dni in lista_dnis:
            dias_venidos.append(row.fecha)
            dias_cont_venidos += 1

    return '\n'.join(dias_venidos)

def ordenar_usuarios() -> None:
    'ordena los usuarios alfabéticamente'
    df_usuarios = pd.read_excel(USUARIOS_ARCH).set_index('DNI')
    # ordena todas las filas de usuarios por nombre
    df_usuarios = df_usuarios.sort_values(by=['nombre'])

    try:
        df_usuarios.to_excel(USUARIOS_ARCH)
    except:
        raise PermissionError('por favor cierre el archivo usuarios.xlsx para poder guardar los cambios')

def meses_adeudados(dni_usr:str) -> str:
    'asumiento que el DNI pertenece a la base de datos, devuelve una lista de los meses en los que esa persona vino y no pagó'
    lista_meses_adeudados = []

    df_reg_deudas = pd.read_excel(REG_DEUDOR_ARCH, dtype=str, keep_default_na=False).set_index('mes')
    # mes       |   vinieron    |   pagaron
    # 08/2023       zodaka,juan     zodaka
    
    # en vez de tener nombres en el archivo tendremos DNI's
    for mes, row in df_reg_deudas.iterrows():
        vinieron_ese_mes = row['vinieron'].split()
        pagaron_ese_mes = row['pagaron'].split()

        if dni_usr in vinieron_ese_mes and dni_usr not in pagaron_ese_mes:
            lista_meses_adeudados.append(mes)

    return lista_meses_adeudados

def pagar(mes:str, dni_usr:str) -> str:
    'paga la cuota mensual de un cliente, si se especifica el mes se puede pagar a pasado y futuro, sino se toma el mes actual'
    if mes == '':
        mes = MES

    if dni_usr not in USUARIOS_TOTAL:
        return f'El dni: {dni_usr} no pertenece a la base de datos de usuarios.'
    
    df_reg_deudas = pd.read_excel(REG_DEUDOR_ARCH, dtype=str).set_index('mes')
    
    if mes not in df_reg_deudas.index:
        df_reg_deudas.loc[mes, 'pagaron'] = dni_usr
    else:
        pagados = df_reg_deudas.loc[mes, 'pagaron'].split()

        if dni_usr in pagados: 
            return 'El cliente ya pagó el mes.'
        
        pagados.append(dni_usr)
        df_reg_deudas.loc[mes, 'pagaron'] = ' '.join(pagados)

    try:
        df_reg_deudas.to_excel(REG_DEUDOR_ARCH)
        return f'Realizado con éxito el pago del mes {mes} para el DNI: {dni_usr}'
    except:
        return 'Por favor cierre el archivo reg_deudor.xlsx para poder guardar los cambios.'

def deudores() -> list:
    'devuelve una lista de tuplas ordenada de la forma (meses_adeudados:int, DNI:str)'
    lista_deudores_ord = []

    # esto podría hacerse con list comprehension pero porlas lo dejo así
    for dni in USUARIOS_TOTAL:
        meses = len(meses_adeudados(dni))
        if meses > 0:
            lista_deudores_ord.append([dni, NOMBRES_POR_DNI[dni], meses])

    return lista_deudores_ord

def actualizar_reg_deudor() -> str:
    'a partir de la lectura del archivo de registro diario actualiza el reg_deudor para poner aquellos clientes que hayan ingresado al gym hasta entonces'
    # [ ( mes, [dni] ) ]
    df_reg_hist = pd.read_excel(REG_DIARIO_ARCH, dtype=str).set_index('fecha')
    ingr_por_mes = {}
    vinieron_por_mes = {}

    # genero un diccionario ingr_por_mes de [mes, DNIS] 
    # en el que está escrito el DNI de una persona por cada vez que ingresó ese mes
    for fecha, row in df_reg_hist.iterrows():
        # parseo el mes -y el año-
        mes:str = fecha[3:]  
        dnis:list = row['dnis'].split()
        
        if mes in ingr_por_mes:
            ingr_por_mes[mes].extend(dnis)
        else:
            ingr_por_mes[mes] = dnis

    for mes, dnis in ingr_por_mes.items():
        vinieron = []           # lista de DNI's
        cant_veces_ingr = {}    # contador de veces de ingreso
        
        # cuento la cantidad de días que vino tal DNI
        for dni in dnis:
            if dni in cant_veces_ingr:
                cant_veces_ingr[dni] += 1
            else:
                cant_veces_ingr[dni] = 1

        for dni, veces in cant_veces_ingr.items():
            if veces >= DIAS_PARA_CONTAR_PRESENCIA:
                vinieron.append(dni)

        vinieron_por_mes[mes] = vinieron

    df_reg_deudor = pd.read_excel(REG_DEUDOR_ARCH).set_index('mes')

    for mes, dnis in vinieron_por_mes.items(): df_reg_deudor.loc[mes, 'vinieron'] = ' '.join(dnis)

    try:
        df_reg_deudor.to_excel(REG_DEUDOR_ARCH)
        return 'Actualizado el registro deudor.'
    except:
        return 'Por favor cierre el archivo reg_deudores.xlsx para poder guardar los datos.'

def totalMes(mes:str) -> str:
    'devuelve la cantidad de personas que pagaron cierto mes MM/AAAA'
    df_reg_deudas = pd.read_excel(REG_DEUDOR_ARCH, dtype=str).set_index('mes')
    
    if mes not in df_reg_deudas.index.tolist():
        return 'Este mes todavía no fue pagado por nadie'

    dnis_que_pagaron = df_reg_deudas.loc[mes,'pagaron'].split()
    
    return f'La cantidad de personas que pagaron el {mes} fueron: {len(dnis_que_pagaron)}.'

def nuevoCliente(nombre, dni, tele, dire, anotaciones) -> str:
    usrs = pd.read_excel(USUARIOS_ARCH).set_index('DNI')
    usrs.loc[dni, 'nombre']         = nombre
    usrs.loc[dni, 'telefono']       = tele 
    usrs.loc[dni, 'domicilio']      = dire
    usrs.loc[dni, 'anotaciones']    = anotaciones

    try:
        usrs.to_excel(USUARIOS_ARCH)
        USUARIOS_TOTAL.append(dni)
        return f'¡Ingreso exitoso de {nombre}!'
    except:
        return 'Por favor cierre el archivo usuarios.xlsx para poder guardar los cambios.'

def cliente(dni:str) -> str:
    info_cliente = buscar_cliente(dni)
    if info_cliente == None: return "Este DNI no fue reconocido en la base de datos."
    res = ""
    tipo_anot, anotaciones = info_cliente.pop()
    
    for tipo_dato, valor in info_cliente:
        res += tipo_dato + ':\t\t' + valor + '\n'
    res += tipo_anot + ':\n\n' + anotaciones
    return res

def adeudado(dni:str) -> str:
    if dni not in USUARIOS_TOTAL:
        return f"El DNI: {dni} no pertenece a la base de datos."
    
    return '\n'.join(meses_adeudados(dni))

#endregion

#region [purple] #! funciones de check de pago

def dir_ip() -> (str|None):
    'obtiene la ip desde donde se ejecuta el programa'
    try:
        response = reqget('https://api.ipify.org')
        ip_address = response.text
    except:
        return None
    
    return ip_address

def check() -> bool:
    '🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊🍊'

    computer_ip = dir_ip()
    if computer_ip == None:
        #! conection error
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