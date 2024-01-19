import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import os

# Nombres de las tablas guardadas para recorrerlas después con un bucle.
tablas = [
    "etiquetas_h1",
    "etiquetas_h2",
    "etiquetas_h3",
    "etiquetas_h4",
    "etiquetas_h5",
    "etiquetas_p",
    "etiquetas_blockquote",
    "etiquetas_a",
    "etiquetas_img_src"
]


#Definicion de la funcion que busca con regex una palabra dentro de un texto
def buscar(palabra,texto):
    #for palabra in palabras
    patron = re.compile(r'\b' + re.escape(palabra) + r'\b', re.IGNORECASE)
    resultado = patron.search(texto)
    return resultado
    

# Declaración de la fBaunción principal
def CargarDatos(urls):

    # Creación de la base de datos y tablas fuera del bucle
    directorio = os.path.dirname(os.path.realpath(__file__))
    bdd = os.path.join(directorio, "BBDD/Scrapingbd")
    mi_conexion = sqlite3.connect(bdd)
    cursor = mi_conexion.cursor()
    for tabla in tablas:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS {} (
                Codigo INTEGER PRIMARY KEY AUTOINCREMENT,
                url VARCHAR(255),
                texto VARCHAR(255)
            )
        '''.format(tabla))
    mi_conexion.close()

    # Iteración sobre las URLs
    for url in urls:
        contenido = requests.get(url)
        txtplano = BeautifulSoup(contenido.text, "html.parser")

        etiquetas = {
            "h1": txtplano.find_all("h1"),
            "h2": txtplano.find_all("h2"),
            "h3": txtplano.find_all("h3"),
            "h4": txtplano.find_all("h4"),
            "h5": txtplano.find_all("h5"),
            "p": txtplano.find_all("p"),
            "blockquote": txtplano.find_all("blockquote"),
            "cite": txtplano.find_all("cite"),
            "a": txtplano.find_all("a"),
            "address": txtplano.find_all("address"),
            "img_src": txtplano.find_all("img", {"src": True})
        }
            
        urls_imagenes = [tag['src'] for tag in etiquetas["img_src"]]
        

        # Obtención de los textos de las etiquetas
        titulos = {key: [tag.get_text() for tag in value] for key, value in etiquetas.items()}
        
        # Inserción de datos en la base de datos
        mi_conexion = sqlite3.connect(bdd)
        cursor = mi_conexion.cursor()
        try:
            for tabla, registro in zip(tablas, titulos.values()):
                for r in registro:
                    cursor.execute(f"INSERT INTO {tabla} (url, texto) VALUES (?, ?)", (url, r))
                for url_imagen in urls_imagenes:
                    cursor.execute("INSERT INTO etiquetas_img_src (url, texto) VALUES (?, ?)", (url, url_imagen))
                mi_conexion.commit()
        except Exception as e:
            print(f"Error: {e}")
            mi_conexion.rollback()
        finally:
            mi_conexion.close()

    # Creación del archivo HTML
    mi_conexion = sqlite3.connect(bdd)
    directorio_archivo = 'C:/Users/AcnerMendezFeliz/OneDrive - Cesur-GCoremsa/Eclipse2/CREADOR-DE-CONTENIDOS-WEB-SCRAPmecaEADOS-/Cargador/Archivos'
    cursor = mi_conexion.cursor()
    with open(os.path.join(directorio_archivo, 'Scripting.html'), 'w', encoding='utf-8') as fichero:
        fichero.write("<!DOCTYPE html>\n")
        fichero.write("<html lang=\"en\">\n")
        fichero.write("<head>\n")
        fichero.write("    <meta charset=\"UTF-8\">\n")
        fichero.write("    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">\n")
        fichero.write("    <title>Scripting</title>\n")
        fichero.write("</head>\n")
        fichero.write("<body>\n")
        fichero.write(f"    <ul>")
        palabra=input("Ingrese una palabra a buscar:")
        for tabla in tablas:
            cursor.execute(f'SELECT texto FROM {tabla} order by Codigo  ')
            datos = cursor.fetchall()
            fichero.write(f"    <h1>{tabla }</h1>\n")
            for dato in datos:
                if buscar(palabra,str(dato[0])):
                        fichero.write(f"    <li>{str(dato[0])}</li>\n")
        fichero.write(f"    </ul>\n")
        fichero.write("</body>\n")
        fichero.write("</html>")

    mi_conexion.close()

# Lista de URLs
urlsl = ("https://picsum.photos/","https://es.wikipedia.org/wiki/Mecanismo_de_Anticitera", "https://es.wikipedia.org/wiki/Baloncesto")

# Paco si alguna etiqueta te sale vacia es porque no tiene la palabra que buscas pero si te fijas si estan completas en la bbdd
# o puede que no depende que url pongas jajajjaj
# y no pongas espaciosantes de escribir la palabra que buscas aunque seguro que todo esto lo sabes  

# Invocación de la función
CargarDatos(urlsl)