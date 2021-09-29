#Convert csv to list by stackoverflow
import csv
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

calcEntropy(cont)