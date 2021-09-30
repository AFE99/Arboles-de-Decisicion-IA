#Convert csv to list by stackoverflow
import csv
import math

tabla = []
with open("./prueba.csv") as csvfile:
    reader = csv.reader(csvfile) # change contents to floats
    for row in reader: # each row is a list
        tabla.append(row)
#Pretty Print de la tabla by stackoverflow
s = [[str(e) for e in row] for row in tabla]
lens = [max(map(len, col)) for col in zip(*s)]
fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
table = [fmt.format(*row) for row in s]
print('\n'.join(table))

#Inicializo listas
list=[] #lista que resguarda las variables existentes en el conjunto D
cont=[] #Lista que contabiliza las apariciones de las variables del conjunto D
#Recorre ultima fila (salteando el encabezado de la misma) para contabilizar la cantidad de apariciones de las variables del conjunto D
for i in range(1,len(tabla)):
    # print(tabla[i][len(tabla[1])-3])
    if (tabla[i][len(tabla[1])-1]) in list:
        aux = list.index(tabla[i][len(tabla[1])-1]) #Posicion de la variable del conjunto D
        cont[aux]=cont[aux]+1 #Contabilizo la variable en una segunda lista (cont)
    else:
        list.append(tabla[i][len(tabla[1])-1]) #Resguardo variable del conjunto D agregandola en una posicion de la lista "list"
        cont.append(1) #Agrego una posicion a la lista "cont" inicializada en 1, por la aparición de la variable
print(list)
print(cont)

def form(a,b): 
    import math
    c = -((a/b)*math.log(a/b,2))
    return(c)


#Definicion de funcion que calcula la Entropia del conjunto D
def calcEntropy(listCant):
    entropy=0 #Inicializo la entropia a cero
    tot = sum(listCant) #Calculo el total
    for i in range(len(listCant)):
        entropy=entropy+form(listCant[i],tot)
    print("La entropia resultante es: "+str(entropy))

def calcEntropyAtr(table):
    entropys = {} #Diccionario donde se cargaran las entropias de cada Atributo

    columnas=len(table[1])-1 #se le resta 1 para no incluir la columna de la clase
    for x in range(1,columnas): #Recorreremos la tabla por columnas para trabajar con cada Atributo por separado, salteamos la primera columna de ID
        valores = {} #Diccionario donde se cargaran los valores necesarios para calcular la entropia del atributo
        for y in range(1,len(table)): #Para recorrer los valores de la columna del atributo en la que estamos posicionados, salteamos la primera fila que es la cabecera
            campo = table[y][x] #Se toma el valor que toma el atributo en esa fila
            if campo in valores: #Pregunta si ya se analizo este valor para inicializarlo a 1 o incrementarlo
                if table[y][columnas] in valores[campo]: #Se consulta si el valor de clase en esa fila ya fue analizado con ese atributo para inicializarlo en 1 o incrementarlo.
                    valores[campo][table[y][columnas]]+=1
                else:
                    valores[campo][table[y][columnas]]=1
                valores[campo]["cantidad"]+=1
            else:
                valores[campo]={"cantidad":1}           
                valores[campo][table[y][columnas]]=1 
        entropys[table[0][x]]=0
        for idx in valores:
            cantidad=valores[idx]["cantidad"]
            valores[idx].pop("cantidad")
            variablesFuncion=[]
            for var in valores[idx]:
                entropys[table[0][x]]+=cantidad/(len(table)-1) * (-valores[idx][var]/cantidad * math.log(valores[idx][var]/cantidad, 2))
        entropys[table[0][x]]=round(entropys[table[0][x]], 3)
    print("Entropia de las variables: ",entropys)



calcEntropy(cont)
calcEntropyAtr(tabla)