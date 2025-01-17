import pandas as pd
from colorama import Fore
from pprint import pprint
from sys import stdout
from funciones_aux import *

stdout.reconfigure(encoding='utf-8')


#// intentar chequear por números de teléfono válidos cuando se crea un nuevo cliente
#// hacer otro archivo fácil de leer en donde aparezcan nombres en el registro histórico en vez de DNI's
#// función que devuelva los últimos 90 o N días que vino un cliente particular (DNI) 
#// función o archivo que ordene alfabéticamente los nombres de los usuarios en usuarios.csv
#// cambiar el nombre de modo registro a modo CHECK IN u MODO INGRESO
#// que diga "por favor ingrese su DNI"
#// intentar cambiar los archivos de csv a exel para poder verlos más facilmente
#// cuando se añade un cliente nuevo hay que reiniciar el programa para poder añadirlo a los ingresantes, sino no lo reconoce
#//  cuando un usuario deja de pagar el mes, entre el primer mes y el tercero diga la cantidad de meses que le queda "debe 1 mes, debe 2 meses, etc"
#//  al llegar al 3er mes "usuario dado de baja, por favor, llame al personal del gimnasio"  
#// hacer una función de pagos que dado un usuario haga que se pague el mes actual o un mes dado como segundo argumento opcional
#// hacer una función que lea el registro histórico y en base a eso genere el reg_deudor de las personas que entraron al gimnasio x mes y quienes lo pagaron al mes



print(Fore.GREEN + 'cargando conexión a internet, esto puede tomar unos segundos si es la primera vez en el día 😴')
print(Fore.RESET)
lista_ingresados_hoy = []

def main():
    #region [red] #? carga de funciones al startup
    ordenar_usuarios()
    crear_reg_con_nombres()
    actualizar_reg_deudor()

    print(Fore.BLUE + 'lista de tareas de inicio completada:\n↣ usuarios ordenados \n↣ registro diario de nombres actualizado \n↣ registro de deudor al día\n\n')
    print('Buen día! 😎','recuerde que escribiendo "ayuda" puede ver la lista de comandos')
    print(Fore.RESET)

    registro()
    #endregion

def registro():
    entrada = input(Fore.BLACK +'MODO CHECK-IN (ingrese dni): ').lower()
    print(Fore.RESET)

    # chequeo si es un DNI
    if entrada in lista_ingresados_hoy:
        print(Fore.YELLOW + 'este cliente ya fue anotado en el día de hoy')
        print(Fore.RESET)
    elif entrada in USUARIOS_TOTAL:
        meses = meses_adeudados(entrada)
        cant_meses_adeudados = len(meses)
        if cant_meses_adeudados == 2:
            print(Fore.YELLOW + 'recuerde que debe 2 meses')
            lista_ingresados_hoy.append(entrada)
            print(Fore.GREEN +'Ingreso exitoso! Proceda 👋')
            print(Fore.RESET)
        elif cant_meses_adeudados == 1:
            print(Fore.YELLOW + 'recuerde que debe 1 mes')
            lista_ingresados_hoy.append(entrada)
            print(Fore.GREEN +'Ingreso exitoso! Proceda 👋')
            print(Fore.RESET)
        elif cant_meses_adeudados >= 3:
            print(Fore.RED + 'usuario dado de baja, por favor, llame al personal del gimnasio')
            print(f'adeuda los meses {" ".join(meses)}')
            print(Fore.RESET)
        else:
            lista_ingresados_hoy.append(entrada)
            print(Fore.GREEN +'Ingreso exitoso! Proceda 👋')
            print(Fore.RESET)
    elif entrada == 'ayuda':
        print(Fore.BLACK)
        pprint(comandos_registro)
        print(Fore.RESET)
    elif entrada == 'descartar':
        try:
            lista_ingresados_hoy.pop()
        except IndexError:
            print(Fore.YELLOW + 'la lista de ingresados de hoy se encuentra vacía 🤨')
            print(Fore.RESET)
    elif entrada == 'hoy':
        for i, usr in enumerate(lista_ingresados_hoy, start=0):
            print(Fore.BLUE + f'cliente n°{i}: {usr}')
        print(Fore.RESET)
    elif entrada == '':
        pass
    elif entrada.split()[0] == 'quitar':
        try:
            indice_borrar = int(entrada.split()[1])
            lista_ingresados_hoy.pop(indice_borrar)
        except:
            print(Fore.YELLOW + 'error: índice fuera de la lista o segundo argumento no numérico (pase un índice de persona a borrar)')
            print(Fore.RESET)
    elif entrada == 'comando':
        print(Fore.GREEN + 'entrando al modo comando...')
        print(Fore.RESET)
        comando()
    elif entrada == 'salir':
        guardar_registro_diario(lista_ingresados_hoy)
        crear_reg_con_nombres()
        exit()
    else:
        try:
            dni_desconocido = int(entrada)
            print(Fore.YELLOW + f'El DNI {dni_desconocido} no está en el sistema, intente de nuevo. si el problema persiste llame al personal del gimnasio')
            print(Fore.RESET)
        except:
            print(Fore.RED + 'comando no reconocido, escriba "ayuda" para ver los comandos')
            print(Fore.RESET)

    registro()

def comando():
    entrada = input(Fore.BLACK + 'MODO COMANDO: ').lower()
    print(Fore.RESET)

    if entrada == 'ayuda':
        print(Fore.BLACK)
        pprint(comandos_comando, width=150)
        print(Fore.RESET)
    elif entrada == 'nombresreg':
        print(Fore.BLUE + 'cargando archivo de registro diario con nombres, esto puede tardar unos segundos...')
        print(Fore.RESET)
        crear_reg_con_nombres()
    elif entrada == 'registro':
        print(Fore.GREEN + 'entrando al modo registro...')
        print(Fore.RESET)
        registro()
    elif entrada == '':
        pass
    elif entrada.split()[0] == 'presencia':
        try:
            ultimos_n_dias = entrada.split()[1]
            dni = entrada.split()[2]

            historial = presencia(ultimos_n_dias, dni)

            for dia in historial:
                print(Fore.BLUE + dia)

            if len(historial) == 0:
                print(Fore.YELLOW + 'el dni ingresado es desconocido o no vino todavia 🤨')
            print(Fore.RESET)
        except:
            print(Fore.YELLOW + 'error: la funcion necesita 2 argumentos de tipo numerico (dias) (DNI)')
            print(Fore.RESET)
    elif entrada.split()[0] == 'cliente':
        try:
            resultado_busq_cliente = buscar_cliente(entrada.split()[1])
            if resultado_busq_cliente == None:
                print(Fore.YELLOW + 'el dni ingresado no se encuentra en la base de datos, intente nuevamente')
                print(Fore.RESET)
            else:
                for dato, valor in resultado_busq_cliente:
                    print(Fore.BLUE + f'{dato}: {valor}')
                print(Fore.RESET)
        except:
            print(Fore.YELLOW + 'error: la funcion necesita 1 argumento de tipo numerico (DNI)')
            print(Fore.RESET)
    elif entrada.split()[0] == 'buscliente':
        try:
            pos_clientes = buscar_cliente_nombre(entrada.split()[1])
            if len(pos_clientes) > 1:
                valores = pos_clientes.pop(0)
                tabla = pd.DataFrame(pos_clientes, columns=valores)
                print(Fore.BLUE + '')
                print(tabla)
                print(Fore.RESET)
            else:
                print(Fore.YELLOW + 'no se ha encontrado ninguna coincidencia 😔')
                print(Fore.RESET)
        except:
            print(Fore.YELLOW + 'error: la funcion necesita 1 argumento de tipo numerico (nombre)')
            print(Fore.RESET)
    elif entrada.split()[0] == 'adeudado':
        try:
            dni_usuario = entrada.split()[1]
            if dni_usuario not in USUARIOS_TOTAL: 
                print(Fore.YELLOW + 'el dni proporcionado no se encuentra en la base de datos')
                print(Fore.RESET)
                comando()
            meses_adeud = meses_adeudados(dni_usuario)
            if len(meses_adeud) == 0:
                print(Fore.BLUE + f'el cliente de dni {dni_usuario} no adeuda ningún mes')
                print(Fore.RESET)
            else:
                print(Fore.BLUE + f'el cliente de dni {dni_usuario} adeuda los meses {meses_adeud}')
                print(Fore.RESET)
        except:
            print(Fore.YELLOW + 'debe proporcionar un DNI como argumento para el comando')
            print(Fore.RESET)
    elif entrada == 'nuevocliente':
        def repetir_nuevo_cliente():
            def crear_cliente():
                print(Fore.BLACK)
                dni = input('DNI: ')
                nombre = input('nombre completo: ')
                telefono = input('telefono: ')
                telefono_fijo = input('telefono fijo: ')
                responsable = input('responsable: ')
                alergias = input('alergias: ')
                nacimiento = input('fecha de nacimiento (DD/MM/AAAA): ')
                domicilio = input('domicilio: ')
                plan = input('gim (1), gim/pilates (2), pilates(3): ')
                print(Fore.RESET)
                try:
                    dni = int(dni)
                    plan = int(plan)

                    telefono_strip = ''
                    for char in telefono:
                        if char in '0123456789':
                            telefono_strip += char

                    if len(telefono_strip) > 10:
                        print(Fore.YELLOW + 'el telefono debe tener un maximo de 10 numeros')
                        print(Fore.RESET)
                        raise Exception
                    if plan > 3 or plan < 1:
                        print(Fore.YELLOW + 'el plan debe ser un número entre 1 y 3 inclusive')
                        print(Fore.RESET)
                        raise Exception
                    if dni < 1000000 or dni > 99999999:
                        print(Fore.YELLOW + 'DNI debe ser un número de 8 dígitos')
                        print(Fore.RESET)
                        raise Exception
                except:
                    print(Fore.YELLOW + 'debe dar un número correcto para el DNI y el plan')
                    res = input('escriba 1 si desea volver a intentar, 2 si desea salir: ')
                    print(Fore.RESET)
                    if res == '1':
                        crear_cliente()
                    else:
                        comando()
                
                if plan == 1:
                    plan = 'gim'
                elif plan == 2:
                    plan = 'gim/pilates'
                else:
                    plan = 'pilates'
                
                return dni, [nombre, telefono, telefono_fijo, responsable, alergias, nacimiento, domicilio, plan]
            
            dni_cliente_nuevo, datos = crear_cliente()
            
            usrs = pd.read_excel(USUARIOS_ARCH)
            usrs = usrs.set_index('DNI')
            usrs.loc[dni_cliente_nuevo] = datos 
            try:
                usrs.to_excel(USUARIOS_ARCH)
                USUARIOS_TOTAL.append(str(dni_cliente_nuevo))
            except:
                print(Fore.RED + 'por favor cierre el archivo usuarios.xlsx para poder guardar los cambios')
                print(Fore.RESET)
                repetir_nuevo_cliente()
        repetir_nuevo_cliente()
        ordenar_usuarios()
    elif entrada.split()[0] == 'pagar':
        # primer argumento dni, segundo argumento (opcional) mes a pagar MM/AAAA
        args = entrada.split()
        args.pop(0)
        try:
            dni_usuario = args[0]
            if len(args) == 2:
                mes_a_pagar = args[1]
                res = pagar_mes(dni_usuario, mes_a_pagar)
                if res == None: comando()
            else:
                mes_a_pagar = MES
                res = pagar_mes(dni_usuario)
                if res == None: comando()
            print(Fore.BLUE + f'se pagó con éxito el mes {mes_a_pagar}')
            print(Fore.RESET)
        except:
            print(Fore.YELLOW + 'debe pasarse al menos un argumento (DNI) o el mes escrito no está adeudado')
            print(Fore.RESET)
    elif entrada.split()[0] == 'totalmes':
        try:
            mes = entrada.split()[1]
            cant_pagos = total_mes(mes)
            print(Fore.BLUE + f'se registraron un total de {cant_pagos} pagos en el mes {mes}')
        except:
            print(Fore.YELLOW + 'el comando require de un argumento que es el mes en formato MM/AAAA')
        print(Fore.RESET)        
    elif entrada == 'deudores':
        lista_deudores = deudores()
        if len(lista_deudores) == 0:
            print(Fore.GREEN + 'no hay deudores 🤞')
        for meses, dni_usuario in lista_deudores:
            print(Fore.BLUE + f'dni: {dni_usuario}  adeudado: {meses} meses')
        print(Fore.RESET)
    elif entrada == 'salir':
        guardar_registro_diario(lista_ingresados_hoy)
        crear_reg_con_nombres()
        exit()
    else:
        print(Fore.RED +'comando no reconocido, escriba "ayuda" para ver los comandos')
        print(Fore.RESET)

    comando()

if __name__ == '__main__' and check():
    print(Fore.BLACK + 'conexión a internet exitosa! 💌')
    print(Fore.RESET)
    main()
else:
    input(Fore.RED + 'contacte al desarrollador ↣  error fatal ☠️')
    print(Fore.RESET)
