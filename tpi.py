#Convert csv to list by stackoverflow
import csv
import math

class GenerarArbol:
    def __init__(self,path):
        
        self.tabla = []  #Tabla original con todos los atributos y clases
        self.entropyD = 0
        self.entropysAtr = {}
        
        with open(path) as csvfile:
            reader = csv.reader(csvfile) # change contents to floats
            for row in reader: # each row is a list
                self.tabla.append(row)

        self.tablaTemp = self.tabla #Tabla temporal donde se almacenara la fraccion de la tabla con la que se esta manejando
        #Pretty Print de la tabla by stackoverflow
        s = [[str(e) for e in row] for row in self.tabla]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        self.tablaPrint = [fmt.format(*row) for row in s]
        print('\n'.join(self.tablaPrint))

        #Inicializo listas
        self.list=[] #lista que resguarda las variables existentes en el conjunto D
        self.cont=[] #Lista que contabiliza las apariciones de las variables del conjunto D
        #Recorre ultima fila (salteando el encabezado de la misma) para contabilizar la cantidad de apariciones de las variables del conjunto D
        for i in range(1,len(self.tabla)):
            # print(self.tabla[i][len(self.tabla[1])-3])
            if (self.tabla[i][len(self.tabla[1])-1]) in self.list:
                aux = self.list.index(self.tabla[i][len(self.tabla[1])-1]) #Posicion de la variable del conjunto D
                self.cont[aux]=self.cont[aux]+1 #Contabilizo la variable en una segunda lista (cont)
            else:
                self.list.append(self.tabla[i][len(self.tabla[1])-1]) #Resguardo variable del conjunto D agregandola en una posicion de la lista "list"
                self.cont.append(1) #Agrego una posicion a la lista "cont" inicializada en 1, por la aparición de la variable
        print(self.list)
        print(self.cont)

    def form(self,a,b): 
        import math
        c = -((a/b)*math.log(a/b,2))
        return(c)

    #Definicion de funcion que calcula la Entropia del conjunto D
    def calcEntropy(self, listCant):
        self.entropyD=0 #Inicializo la entropia a cero
        tot = sum(listCant) #Calculo el total
        for i in range(len(listCant)):
            self.entropyD=self.entropyD+ self.form(listCant[i],tot)
        print("La entropia resultante es: "+str(self.entropyD))

    def calcEntropyAtr(self):
        #Diccionario donde se cargaran las entropias de cada Atributo
        
        columnas=len(self.tablaTemp[1])-1 #se le resta 1 para no incluir la columna de la clase
        for x in range(1,columnas): #Recorreremos la tabla por columnas para trabajar con cada Atributo por separado, salteamos la primera columna de ID
            valores = {} #Diccionario donde se cargaran los valores necesarios para calcular la entropia del atributo
            for y in range(1,len(self.tablaTemp)): #Para recorrer los valores de la columna del atributo en la que estamos posicionados, salteamos la primera fila que es la cabecera
                campo = self.tablaTemp[y][x] #Se toma el valor que toma el atributo en esa fila
                if campo in valores: #Pregunta si ya se analizo este valor para inicializarlo a 1 o incrementarlo
                    if self.tablaTemp[y][columnas] in valores[campo]: #Se consulta si el valor de clase en esa fila ya fue analizado con ese atributo para inicializarlo en 1 o incrementarlo.
                        valores[campo][self.tablaTemp[y][columnas]]+=1
                    else:
                        valores[campo][self.tablaTemp[y][columnas]]=1
                    valores[campo]["cantidad"]+=1
                else:
                    valores[campo]={"cantidad":1}           
                    valores[campo][self.tablaTemp[y][columnas]]=1 
            self.entropysAtr[self.tablaTemp[0][x]]=0
            for idx in valores:
                cantidad=valores[idx]["cantidad"]
                valores[idx].pop("cantidad")

                for var in valores[idx]:
                    self.entropysAtr[self.tablaTemp[0][x]]+=cantidad/(len(self.tablaTemp)-1) * (-valores[idx][var]/cantidad * math.log(valores[idx][var]/cantidad, 2))
            self.entropysAtr[self.tablaTemp[0][x]]=round(self.entropysAtr[self.tablaTemp[0][x]], 3)
        print("Entropia de las variables: ",self.entropysAtr)

    def mejorGanancia(self):
        ganancia= 0

        for e in self.entropysAtr:
            ganAux= self.entropyD - self.entropysAtr[e] 
            if ganAux > ganancia:
                ganancia = ganAux
                Nodo=e

        print("Nodo Raiz según Ganancia: " ,Nodo)


    def AlgoritmoC45(self):
        if False:
            print("primer condición base")
            
        if False:
            print("segunda condición base")

        self.calcEntropy(self.cont)
        self.calcEntropyAtr()
        self.mejorGanancia()




# calcEntropy(cont)
# calcEntropyAtr(tabla)
if __name__ == "__main__":
    Arbol = GenerarArbol("./prueba.csv")
    Arbol.AlgoritmoC45()