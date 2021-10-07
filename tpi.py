#Convert csv to list by stackoverflow
import csv
import math
from pprint import pprint
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
        # print("Atributos: ",self.Atributes)

        print("------------------------------------------------TABLA-----------------------------------------------")
        self.prettyPrint(self.tabla)
        print("----------------------------------------------------------------------------------------------------")
        #Pretty Print de la tabla by stackoverflow
        # s = [[str(e) for e in row] for row in self.tabla]
        # lens = [max(map(len, col)) for col in zip(*s)]
        # fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        # self.tablaPrint = [fmt.format(*row) for row in s]
        # print('\n'.join(self.tablaPrint))
 
    def prettyPrint(self,table):
        s = [[str(e) for e in row] for row in table]
        lens = [max(map(len, col)) for col in zip(*s)]
        fmt = '\t'.join('{{:{}}}'.format(x) for x in lens)
        table = [fmt.format(*row) for row in s]
        print('\n'.join(table))
    
    #Método que contabiliza la cantidad de apariciones del conjunto D 
    def varConjD(self,Tabla):
        #Inicializo listas
        list=[] #lista que resguarda las variables existentes en el conjunto D
        cont=[] #Lista que contabiliza las apariciones de las variables del conjunto D
        #Recorre ultima fila (salteando el encabezado de la misma) para contabilizar la cantidad de apariciones de las variables del conjunto D
        for i in range(1,len(Tabla)):
            if (Tabla[i][len(Tabla[1])-1]) in list:
                aux = list.index(Tabla[i][len(Tabla[1])-1]) #Posicion de la variable del conjunto D
                cont[aux]=cont[aux]+1 #Contabilizo la variable en una segunda lista (cont)
            else:
                list.append(Tabla[i][len(Tabla[1])-1]) #Resguardo variable del conjunto D agregandola en una posicion de la lista "list"
                cont.append(1) #Agrego una posicion a la lista "cont" inicializada en 1, por la aparición de la variable
        # print(list)
        # print(cont)
        return cont

    def form(self,a,b): 
        import math
        c = -((a/b)*math.log(a/b,2))
        return(c)

    #Definicion de funcion que calcula la Entropia del conjunto D
    def calcEntropy(self,listCant):
        entropyD=0 #Inicializo la entropia a cero
        tot = sum(listCant) #Calculo el total
        for i in range(len(listCant)):
            entropyD=entropyD+ self.form(listCant[i],tot)
        print("\n La entropia del conjunto D es: "+str(entropyD))
        return(entropyD)

    def calcEntropyAtr(self,Tabla,Atributes):
        #Diccionario donde se cargaran las entropias de cada Atributo
        # self.Atributes.remove("Colesterol")
        # self.Atributes.remove("Edad")
        columnas=len(Tabla[1])-1
        entropysAtr = {}
        # print(Atributes)
        print("-----------------------------------------------------------------------------------------------------")
        print("VALORES: ")
        for x in range(len(Atributes)): #Recorreremos la tabla por columnas para trabajar con cada Atributo por separado, salteamos la primera columna de ID
            Atr = Tabla[0].index(Atributes[x])
            print("\n",Tabla[0][Atr])
            valores = {} #Diccionario donde se cargaran los valores necesarios para calcular la entropia del atributo
            for y in range(1,len(Tabla)): #Para recorrer los valores de la columna del atributo en la que estamos posicionados, salteamos la primera fila que es la cabecera
                campo = Tabla[y][Atr] #Se toma el valor que toma el atributo en esa fila
                if campo in valores: #Pregunta si ya se analizo este valor para inicializarlo a 1 o incrementarlo
                    if Tabla[y][columnas] in valores[campo]: #Se consulta si el valor de clase en esa fila ya fue analizado con ese atributo para inicializarlo en 1 o incrementarlo.
                        valores[campo][Tabla[y][columnas]]+=1
                    else:
                        valores[campo][Tabla[y][columnas]]=1
                    valores[campo]["cantidad"]+=1
                else:
                    valores[campo]={"cantidad":1}           
                    valores[campo][Tabla[y][columnas]]=1 
            entropysAtr[Tabla[0][Atr]]={"entropia":0,"Djs":[],"Vars":[]}
            pprint(valores, width=1)
            for idx in valores:
                #print(idx,valores)
                if idx not in  entropysAtr[Tabla[0][Atr]]["Vars"]:
                        entropysAtr[Tabla[0][Atr]]["Vars"].append(idx)
                cantidad=valores[idx]["cantidad"]
                valores[idx].pop("cantidad")
                
                entropysAtr[Tabla[0][Atr]]["Djs"].append(cantidad)
                for var in valores[idx]:
                    #print(var,valores[idx],valores[idx][var])
                    entropysAtr[Tabla[0][Atr]]["entropia"]+=cantidad/(len(Tabla)-1) * (-valores[idx][var]/cantidad * math.log(valores[idx][var]/cantidad, 2))
            entropysAtr[Tabla[0][Atr]]["entropia"]=round(entropysAtr[Tabla[0][Atr]]["entropia"], 3)
        print("-----------------------------------------------------------------------------------------------------")
        print("Entropia de las variables: ")
        pprint(entropysAtr, width=1)
        return entropysAtr

    # Funcion que calcula quien seria el siguiente nodo segun la ganancia y/o tasa de ganancia
    def mejorGananciayTasa(self,pg,entropysAtr,Tabla):
        ganancia= 0
        Tasaganancia= 0
        tasaAux=0

        for e in entropysAtr:
            ganAux= pg - entropysAtr[e]["entropia"]
            if ganAux > ganancia:
                ganancia = ganAux
                NodoG=e
            
            for Dj in entropysAtr[e]["Djs"]:
                tasaAux+=-Dj/(len(Tabla)-1) * math.log(Dj/(len(Tabla)-1), 2)
            # print(ganAux,tasaAux,"pri")
            tasaAux=ganAux/tasaAux
            
            if tasaAux > Tasaganancia:
                Tasaganancia = tasaAux
                NodoTG=e
            # print(tasaAux,"seg")
        print("-----------------------------------------------------------------------------------------------------")
        print("Nodo Raiz según Ganancia: " ,NodoG, "\nNodo Raiz según Tasa Ganancia: ",NodoTG)
        print("*****************************************************************************************************")
        return NodoG

    def ObtenerParticion(self,Tabla,Atributo,Variable):
        tablaTemp2 = [Tabla[0]]

        column = Tabla[0].index(Atributo)

        for x in range(1,len(Tabla)):
            #print(contador,rows,Tabla[x][column],Variable)
            if Tabla[x][column] == Variable:
                tablaTemp2.append(Tabla[x])
        
        return tablaTemp2

    def ExamplesSameClass(self,Tabla):
        # print("TABLA",Tabla)
        rows=len(Tabla)
        columnClass= len(Tabla[0])-1
        # print(columnClass)
        marca=""
        if rows>1:
            marca=Tabla[1][columnClass]
            for x in range(2,len(Tabla)):
                # print("MARCA: ",marca,Tabla[x][columnClass])
                if marca!=Tabla[x][columnClass]:
                    return False
        self.NodeSheet = marca
        return True

    def ValorMasFreq(self, Tabla):
        columnClass= len(Tabla[0])-1
        valores = {}
        for x in range(1,len(Tabla)):
            if Tabla[x][columnClass] in valores:
                valores[Tabla[x][columnClass]]+= 1
            else:
                valores[Tabla[x][columnClass]] = 1
        marca = 0
        for x in valores:
            if valores[x]>marca:
                marca = valores[x]
                valorMasFreq = x
        
        return valorMasFreq

    def AlgoritmoC45(self,Tabla,Atributes,Tree):
        
        if self.ExamplesSameClass(Tabla):
            Tree.append(self.NodeSheet)
            # Tree.append(Node(self.NodeSheet,self.NodeParent["parent"]))
            # self.NodeParent.setChild[Tree[len(Tree)-1],self.NodeParent["branch"]]
        elif len(Atributes) == 0:
            print("No hay mas atributos a analizar, tabla= ", pprint(Tabla, width=1))
            # print(Tabla)
            
            Tree.append(self.ValorMasFreq(Tabla))
            # for x in Tree:
            #     print(x.getName())
            #     print(x.getChild())
            #     print(x.getParent())
        else:
            pg= self.calcEntropy(self.varConjD(Tabla))

            EntropysAtr = self.calcEntropyAtr(Tabla,Atributes)
            # print(EntropysAtr)
            Ag = self.mejorGananciayTasa(pg,EntropysAtr,Tabla)

            if False:
                print("threshold section")
            else:
                #Tree.append(Node(Ag,self.NodeParent["parent"]))
                Tree.append(Ag)
                # if self.NodeParent["parent"]!= None:
                #     print(self.NodeParent["branch"])
                #     print(self.NodeParent["parent"].getChild())
                #     self.NodeParent["parent"].setChild(Tree[len(Tree)-1],self.NodeParent["branch"])
                # self.NodeParent["parent"] = Tree[len(Tree)-1]
                # print(self.NodeParent["parent"].getChild())
                
                #print(self.tabla)
                Dpartition = []
                # print(EntropysAtr[Ag]["Vars"])
                for var in EntropysAtr[Ag]["Vars"]:
                    Dpartition.append(self.ObtenerParticion(Tabla,Ag,var))
                print("\nDpartition = ")
                for i in range(len(Dpartition)):
                    for j in range(len(Dpartition[i])):
                        print(Dpartition[i][j])
                # print(Dpartition)
                # print(Ag,Atributes)
                Atributes.remove(Ag)
                for Dj in range(len(Dpartition)):
                    Tree.append(EntropysAtr[Ag]["Vars"][Dj])
                    # self.NodeParent["branch"] = EntropysAtr[Ag]["Vars"][Dj]
                    # print(self.NodeParent["branch"])
                    # input()
                    # Tree[len(Tree)-1].setChild(None,EntropysAtr[Ag]["Vars"][Dj])
                    
                    Tabla = Dpartition[Dj]
                    # print("ENTREEE")
                    self.AlgoritmoC45(Tabla,Atributes,Tree)
                
                #print(Tree[0].getChild())
        print("\nArbol: ",Tree)
        print("\n Los atributos identificados son: ",Atributes,len(Atributes))           



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
    Arbol = GenerarArbol("./prueba6.csv")
    Arbol.AlgoritmoC45(Arbol.tabla,Arbol.Atributes,Arbol.Tree)