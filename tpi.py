#Convert csv to list by stackoverflow
import csv
import math

class GenerarArbol:
    def __init__(self,path):
        
        self.tabla = []  #Tabla original con todos los atributos y clases
        self.entropyD = 0
        self.entropysAtr = {}
        self.Tree = []
        self.NodeSheet = ""
        self.NodeParent = {"parent":None,"branch":None}        

        with open(path) as csvfile:
            reader = csv.reader(csvfile) # change contents to floats
            for row in reader: # each row is a list
                self.tabla.append(row)
        self.columnas=len(self.tabla[1])-1 #se le resta 1 para no incluir la columna de la clase
        self.tablaTemp = self.tabla #Tabla temporal donde se almacenara la fraccion de la tabla con la que se esta manejando

        self.Atributes = []

        for x in range(1,len(self.tabla[1])-1):
            self.Atributes.append(self.tabla[0][x])
        print(self.Atributes)

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
        # self.entropyD=0 #Inicializo la entropia a cero
        tot = sum(listCant) #Calculo el total
        for i in range(len(listCant)):
            self.entropyD=self.entropyD+ self.form(listCant[i],tot)
        print("La entropia resultante es: "+str(self.entropyD))
        return(self.entropyD)

    def calcEntropyAtr(self):
        #Diccionario donde se cargaran las entropias de cada Atributo
        # self.Atributes.remove("Colesterol")
        # self.Atributes.remove("Edad")
        self.entropysAtr = {}
        print(self.Atributes)
        for x in range(len(self.Atributes)): #Recorreremos la tabla por columnas para trabajar con cada Atributo por separado, salteamos la primera columna de ID
            Atr = self.tabla[0].index(self.Atributes[x])
            print(Atr)
            valores = {} #Diccionario donde se cargaran los valores necesarios para calcular la entropia del atributo
            for y in range(1,len(self.tablaTemp)): #Para recorrer los valores de la columna del atributo en la que estamos posicionados, salteamos la primera fila que es la cabecera
                campo = self.tablaTemp[y][Atr] #Se toma el valor que toma el atributo en esa fila
                if campo in valores: #Pregunta si ya se analizo este valor para inicializarlo a 1 o incrementarlo
                    if self.tablaTemp[y][self.columnas] in valores[campo]: #Se consulta si el valor de clase en esa fila ya fue analizado con ese atributo para inicializarlo en 1 o incrementarlo.
                        valores[campo][self.tablaTemp[y][self.columnas]]+=1
                    else:
                        valores[campo][self.tablaTemp[y][self.columnas]]=1
                    valores[campo]["cantidad"]+=1
                else:
                    valores[campo]={"cantidad":1}           
                    valores[campo][self.tablaTemp[y][self.columnas]]=1 
            self.entropysAtr[self.tablaTemp[0][Atr]]={"entropia":0,"Djs":[],"Vars":[]}
            print("VALORESSSS",valores)
            for idx in valores:
                #print(idx,valores)
                if idx not in  self.entropysAtr[self.tablaTemp[0][Atr]]["Vars"]:
                        self.entropysAtr[self.tablaTemp[0][Atr]]["Vars"].append(idx)
                cantidad=valores[idx]["cantidad"]
                valores[idx].pop("cantidad")
                
                self.entropysAtr[self.tablaTemp[0][Atr]]["Djs"].append(cantidad)
                for var in valores[idx]:
                    #print(var,valores[idx],valores[idx][var])
                    self.entropysAtr[self.tablaTemp[0][Atr]]["entropia"]+=cantidad/(len(self.tablaTemp)-1) * (-valores[idx][var]/cantidad * math.log(valores[idx][var]/cantidad, 2))
            self.entropysAtr[self.tablaTemp[0][Atr]]["entropia"]=round(self.entropysAtr[self.tablaTemp[0][Atr]]["entropia"], 3)
        print("Entropia de las variables: ",self.entropysAtr)

    def mejorGananciayTasa(self):
        ganancia= 0
        Tasaganancia= 0
        tasaAux=0

        for e in self.entropysAtr:
            ganAux= self.entropyD - self.entropysAtr[e]["entropia"]
            if ganAux > ganancia:
                ganancia = ganAux
                NodoG=e
            
            for Dj in self.entropysAtr[e]["Djs"]:
                tasaAux+=-Dj/(len(self.tablaTemp)-1) * math.log(Dj/(len(self.tablaTemp)-1), 2)
            # print(ganAux,tasaAux,"pri")
            tasaAux=ganAux/tasaAux
            
            if tasaAux > Tasaganancia:
                Tasaganancia = tasaAux
                NodoTG=e
            # print(tasaAux,"seg")

        print("Nodo Raiz según Ganancia: " ,NodoG, " Nodo Raiz según Tasa Ganancia: ",NodoTG)

        return NodoG
    def ObtenerParticion(self,Atributo,Variable):
        self.tablaTemp2 = [self.tablaTemp[0]]

        column = self.tablaTemp[0].index(Atributo)

        for x in range(1,len(self.tablaTemp)):
            #print(contador,rows,self.tablaTemp[x][column],Variable)
            if self.tablaTemp[x][column] == Variable:
                self.tablaTemp2.append(self.tablaTemp[x])
        
        return self.tablaTemp2

    def ExamplesSameClass(self):
        rows=len(self.tablaTemp)
        marca=""
        if rows>2:
            marca=self.tablaTemp[1]
            for x in range(2,len(self.tablaTemp)):
                if marca!=self.tablaTemp[x]:
                    
                    return False
        self.NodeSheet = marca
        return True

    def AlgoritmoC45(self,Atributes):
        print("ATRIBUTOSS",Atributes,len(Atributes))
        if self.ExamplesSameClass():
            self.Tree.append(self.NodeSheet)
            # self.Tree.append(Node(self.NodeSheet,self.NodeParent["parent"]))
            # self.NodeParent.setChild[self.Tree[len(self.Tree)-1],self.NodeParent["branch"]]
        elif len(Atributes) == 0:
            print(self.Tree)
            # for x in self.Tree:
            #     print(x.getName())
            #     print(x.getChild())
            #     print(x.getParent())
        else:
            pg= self.calcEntropy(self.cont)

            self.calcEntropyAtr()

            Ag = self.mejorGananciayTasa()

            if False:
                print("threshold section")
            else:
                #self.Tree.append(Node(Ag,self.NodeParent["parent"]))
                self.Tree.append(Ag)
                # if self.NodeParent["parent"]!= None:
                #     print(self.NodeParent["branch"])
                #     print(self.NodeParent["parent"].getChild())
                #     self.NodeParent["parent"].setChild(self.Tree[len(self.Tree)-1],self.NodeParent["branch"])
                # self.NodeParent["parent"] = self.Tree[len(self.Tree)-1]
                # print(self.NodeParent["parent"].getChild())
                
                #print(self.tabla)
                Dpartition = []
                print(self.entropysAtr[Ag]["Vars"])
                for var in self.entropysAtr[Ag]["Vars"]:
                    Dpartition.append(self.ObtenerParticion(Ag,var))
                print(Dpartition)
                
                print(Ag,Atributes)
                self.Atributes.remove(Ag)
                for Dj in range(len(Dpartition)):
                    self.Tree.append(self.entropysAtr[Ag]["Vars"][Dj])
                    # self.NodeParent["branch"] = self.entropysAtr[Ag]["Vars"][Dj]
                    # print(self.NodeParent["branch"])
                    # input()
                    # self.Tree[len(self.Tree)-1].setChild(None,self.entropysAtr[Ag]["Vars"][Dj])
                    
                    self.tablaTemp = Dpartition[Dj]
                    print("ENTREEE")
                    self.AlgoritmoC45(Atributes)
                
                #print(self.Tree[0].getChild())
                print(self.Tree)



class Node:

    def __init__(self, name, parent):
        self.name = name
        self.parent = parent
        self.child = {}

        # Métodos para asignar nodos

    # def setName(self,name):
    #     self.name = name

    def getName(self):
        return self.name

    def getParent(self):
        return self.parent
    
    def setChild(self,child,branch):
        self.child[branch] = child
    
    def getChild(self):
        return self.child





# calcEntropy(cont)
# calcEntropyAtr(tabla)
if __name__ == "__main__":
    Arbol = GenerarArbol("./prueba.csv")
    Arbol.AlgoritmoC45(Arbol.Atributes)