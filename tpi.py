#Convert csv to list by stackoverflow
import csv
from logging import error
import math
import copy
import os
from tkinter.constants import CENTER
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
import pygraphviz as pgv
from pprint import pprint
# from tkinter import IntVar, Radiobutton, ttk
from tkinter import *
import tkinter as tk
from tkinter import scrolledtext as st
from tkinter import filedialog as fd
from tkinter import messagebox
from tkinter import ttk
import cv2

class GenerarArbol:
    def __init__(self,path):

        self.tabla = []  #Tabla original con todos los atributos y clases
        self.TreexGan = True
        self.entropyD = 0
        self.entropysAtr = {}
        self.Tree = []
        self.NodeSheet = ""
        self.threshold = 0
        self.NodeParent = {"parent":None,"branch":None,"nodo":None}
        self.G=pgv.AGraph(directed=True)
        
        try:
            with open(path) as csvfile:
                reader = csv.reader(csvfile) # change contents to floats
                for row in reader: # each row is a list
                    self.tabla.append(row)
        except:
            messagebox.showwarning(message="Por favor, ingrese un archivo correcto", title="Error de formato")
        self.columnas=len(self.tabla[1])-1 #se le resta 1 para no incluir la columna de la clase

        self.Atributes = []

        for x in range(1,len(self.tabla[1])-1):
            self.Atributes.append(self.tabla[0][x])

        # print("------------------------------------------------TABLA-----------------------------------------------")
        # self.prettyPrint(self.tabla)
        # print("----------------------------------------------------------------------------------------------------")

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
        # print("\n La entropia del conjunto D es: "+str(entropyD))
        return(entropyD)

    def calcEntropyAtr(self,Tabla,Atributes):
        columnas=len(Tabla[1])-1
        entropysAtr = {} #Diccionario donde se cargaran las entropias de cada Atributo
        # print(Atributes)
        # print("-----------------------------------------------------------------------------------------------------")
        # print("VALORES: ")
        for x in range(len(Atributes)): #Recorreremos la tabla por columnas para trabajar con cada Atributo por separado, salteamos la primera columna de ID
            Atr = Tabla[0].index(Atributes[x])
            # print("\n",Tabla[0][Atr])
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
            # pprint(valores, width=1)
            for idx in valores:
                if idx not in  entropysAtr[Tabla[0][Atr]]["Vars"]:
                        entropysAtr[Tabla[0][Atr]]["Vars"].append(idx)
                cantidad=valores[idx]["cantidad"]
                valores[idx].pop("cantidad")

                entropysAtr[Tabla[0][Atr]]["Djs"].append(cantidad)
                for var in valores[idx]:
                    entropysAtr[Tabla[0][Atr]]["entropia"]+=cantidad/(len(Tabla)-1) * (-valores[idx][var]/cantidad * math.log(valores[idx][var]/cantidad, 2))
            entropysAtr[Tabla[0][Atr]]["entropia"]=round(entropysAtr[Tabla[0][Atr]]["entropia"], 3)
        # print("-----------------------------------------------------------------------------------------------------")
        # print("Entropia de las variables: ")
        # pprint(entropysAtr, width=1)
        return entropysAtr

    # Funcion que calcula quien seria el siguiente nodo segun la ganancia y/o tasa de ganancia
    def mejorGananciayTasa(self,p0,entropysAtr,Tabla):
        ganancia= 0
        Tasaganancia= 0
        tasaAux=0

        for e in entropysAtr:
            ganAux= p0 - entropysAtr[e]["entropia"]
            if ganAux > ganancia:
                ganancia = ganAux
                NodoG=e

            for Dj in entropysAtr[e]["Djs"]: #Calcula la tasa de ganancia para el atributo "e" del ciclo for
                tasaAux+=-Dj/(len(Tabla)-1) * math.log(Dj/(len(Tabla)-1), 2)
            if tasaAux != 0 :
                tasaAux=round(ganAux/tasaAux,3)

            if tasaAux > Tasaganancia:
                Tasaganancia = tasaAux
                NodoTG=e
            tasaAux=0
        # print("-----------------------------------------------------------------------------------------------------")
        # print("Nodo Raiz según Ganancia: " ,NodoG, "\nNodo Raiz según Tasa Ganancia: ",NodoTG)
        # print("*****************************************************************************************************")
        
        if self.TreexGan:
            return NodoG
        else: 
            return NodoTG

    def ObtenerParticion(self,Tabla,Atributo,Variable):
        tablaTemp2 = [Tabla[0]]

        column = Tabla[0].index(Atributo)

        for x in range(1,len(Tabla)):
            if Tabla[x][column] == Variable:
                tablaTemp2.append(Tabla[x])

        return tablaTemp2

    def ExamplesSameClass(self,Tabla):
        rows=len(Tabla)
        columnClass= len(Tabla[0])-1
        marca=""
        if rows>1:
            marca=Tabla[1][columnClass]
            for x in range(2,len(Tabla)):
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
            # Tree[0].append(self.NodeSheet)
            if Tree[1]["nodo"]==None:
                Tree[1]["parent"]=Atributes[0]
                Tree[1]["nodo"]=Node(Atributes[0],None)
                Tree[1]["branch"]=Tabla[1][1]
            self.G.add_node("Nodo%i"%len(Tree[0]),label=self.NodeSheet, color='green')
            self.G.add_edge(Tree[1]["parent"],"Nodo%i"%len(Tree[0]), color='black',label=Tree[1]["branch"])
            Tree[0].append(Node(self.NodeSheet,Tree[1]["nodo"]))
            Tree[1]["nodo"].setChild(Tree[0][len(Tree[0])-1],Tree[1]["branch"])
        elif len(Atributes) == 0:
            # print("No hay mas atributos a analizar, tabla= ", pprint(Tabla, width=1))

            # Tree[0].append(self.ValorMasFreq(Tabla))
            self.G.add_node("Nodo%i"%len(Tree[0]),label=self.ValorMasFreq(Tabla), color='green')
            self.G.add_edge(Tree[1]["parent"],"Nodo%i"%len(Tree[0]), color='black',label=Tree[1]["branch"])
           
            Tree[0].append(Node(self.ValorMasFreq(Tabla),Tree[1]["nodo"]))            
            Tree[1]["nodo"].setChild(Tree[0][len(Tree[0])-1],Tree[1]["branch"])
        else:
            NodeParent = copy.deepcopy(Tree[1])

            p0= self.calcEntropy(self.varConjD(Tabla)) #Se almacena la entropia del conjunto D

            EntropysAtr = self.calcEntropyAtr(Tabla,Atributes)

            Ag = self.mejorGananciayTasa(p0,EntropysAtr,Tabla)

            if p0 - EntropysAtr[Ag]["entropia"] < self.threshold and NodeParent["parent"] != None:
                # Tree[0].append(self.ValorMasFreq(Tabla))
                self.G.add_node("Nodo%i"%len(Tree[0]),label=self.ValorMasFreq(Tabla), color='pink')
                self.G.add_edge(Tree[1]["parent"],"Nodo%i"%len(Tree[0]), color='pink',label=Tree[1]["branch"])
                Tree[0].append(Node(self.ValorMasFreq(Tabla),Tree[1]["nodo"]))            
                Tree[1]["nodo"].setChild(Tree[0][len(Tree[0])-1],Tree[1]["branch"])
            else:
                # Tree[0].append(Ag)
                Tree[0].append(Node(Ag,NodeParent["nodo"]))
                if NodeParent["parent"]== None:
                    self.G.add_node(Ag, color='red')
                    NodeParent["parent"] = Ag
                else:
                    self.G.add_node("Nodo%i"%len(Tree[0]),label=Ag, color='blue')
                    self.G.add_edge(NodeParent["parent"],"Nodo%i"%len(Tree[0]), color='black',label=NodeParent["branch"])
                    NodeParent["parent"] = "Nodo%i"%len(Tree[0])
                    Tree[1]["nodo"].setChild(Tree[0][len(Tree[0])-1],NodeParent["branch"])
                    # print(NodeParent["nodo"].getName(),"asddddddddddddddddddd",NodeParent["branch"])

                NodeParent["nodo"] = Tree[0][len(Tree[0])-1]

                Dpartition = []
                for var in EntropysAtr[Ag]["Vars"]:
                    Dpartition.append(self.ObtenerParticion(Tabla,Ag,var))
                # print("\nDpartition = ")
                # for i in range(len(Dpartition)):
                #     for j in range(len(Dpartition[i])):
                #         print(Dpartition[i][j])

                Atributes2 = copy.deepcopy(Atributes)
                Atributes2.remove(Ag)

                for Dj in range(len(Dpartition)):
                    Tree[0].append(EntropysAtr[Ag]["Vars"][Dj])
                    NodeParent["branch"] = EntropysAtr[Ag]["Vars"][Dj]
                    # Tree[len(Tree)-1].setChild(None,EntropysAtr[Ag]["Vars"][Dj])
                    # Tree[0][len(Tree[0])-1].setChild(None,EntropysAtr[Ag]["Vars"][Dj])
                    Tabla = Dpartition[Dj]
                    self.AlgoritmoC45(Tabla,Atributes2,[Tree[0],NodeParent])

        return Tree[0]
        # print("\n Los atributos identificados son: ",Atributes,len(Atributes))

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

class GraphicInterface:
    def __init__(self, master,tk):
        self.contenido=None #Variable que guardará la ruta del archivo a abrir
        self.threshold=0 #Variable que guardará el valor del TH ingresado, por default comienza en 0
        self.master = master
        self.agregar_menu()
        self.ArbolGain=[]
        self.ArbolGainRatio=[]
        self.TablaTesteo=[]
        self.NuevaInstancia=[]
        self.botonValue=None
        self.valorAtribute=[]
        self.win= None
        self.value= None
        # self.scrolledtext1=st.ScrolledText(self.master, width=80, height=20)
        # self.scrolledtext1.grid(column=0,row=0, padx=10, pady=10)   

        self.master.title("TPI Inteligencia Artificial - Grupo 9")
		# self.master.iconbitmap()
        self.master.resizable(0,0)

        w=550
        h=350
        ws = self.master.winfo_screenwidth()
        hs = self.master.winfo_screenheight()
        # calculate position x, y
        x = (ws/2) - (w/2)    
        y = (hs/2) - (h/2)
        self.master.geometry('%dx%d+%d+%d' % (w, h, x, y))
        
        # self.master.geometry("550x350")
        self.frameInicio = tk.Frame(self.master, width=400, height=250,bg="#9BBCD1",relief="groove", borderwidth=5)
        self.frameInicio.pack(fill="both",side="top",expand="YES")

        self.Titulo=tk.Label(self.frameInicio,bg="#9BBCD1",text="TPI - Inteligencia Artificial - Grupo 9",fg="black",height=2,font=("Ubuntu",22))

        self.Integrantes = tk.Label(self.frameInicio,bg="#9BBCD1",text="Integrantes:",fg="black",height=2,font=("Ubuntu",15))
        self.Integrante1 = tk.Label(self.frameInicio,bg="#9BBCD1",text="Acevedo, Fernando Enrique",fg="black",height=1,font=("Ubuntu",10))
        self.Integrante2= tk.Label(self.frameInicio,bg="#9BBCD1",text="Figueroa, Simon",fg="black",height=1,font=("Ubuntu",10))
        self.Integrante3 = tk.Label(self.frameInicio,bg="#9BBCD1",text="Ortiz, Claudia",fg="black",height=1,font=("Ubuntu",10))
        self.Integrante4 = tk.Label(self.frameInicio,bg="#9BBCD1",text="Soto, Juan Cruz",fg="black",height=1,font=("Ubuntu",10))
        self.botonIniciar=tk.Button(self.frameInicio, text="Iniciar",bg="#2D373D",fg="#42D5FF",width=20,height=0,command=lambda:self.MenuPrincipal())
        

        self.Titulo.grid(row=0,column=0,columnspan=5,padx=20,pady=10)
        self.Integrantes.grid(row=1,column=1,columnspan=3)
        self.Integrante1.grid(row=2,column=1,columnspan=3)
        self.Integrante2.grid(row=3,column=1,columnspan=3)
        self.Integrante3.grid(row=4,column=1,columnspan=3)
        self.Integrante4.grid(row=5,column=1,columnspan=3)
        self.botonIniciar.grid(row=6,column=2,padx=0,pady=10)

    def agregar_menu(self):
        menubar1 = tk.Menu(self.master)
        self.master.config(menu=menubar1)
        opciones1 = tk.Menu(menubar1, tearoff=0)
        menubar1.add_cascade(label="Abrir Archivo", command=self.abrirAr)

    def abrirAr(self):
        nombrearch=fd.askopenfilename(initialdir = os.path.abspath(os.getcwd()),title = "Seleccione archivo",filetypes = (("Archivos CSV","*.csv"),("Todos los archivos","*.*")))
        if nombrearch!='':
            self.contenido=nombrearch
            

    def actualizarFile(self,datoFile,opc):
        fileant = self.contenido
        self.abrirAr()
        datoFile.set(self.contenido)
        if fileant != self.contenido:
            self.actualizargrafico(opc)
    
    def actualizarTh(self,th,opc):
        # try:
        th = float(th)
        if th!=self.threshold:
            self.threshold = th
            self.actualizargrafico(opc)
        # except:
        #     messagebox.showerror(message="Por favor, ingrese un valor valido", title="ERROR",parent=self.raiz)

    def Cerrar(self):
        self.botonIniciar["state"]="normal"
        self.raiz.destroy()

    def MenuPrincipal(self):
        if self.contenido!=None:
            self.botonIniciar["state"]="disabled"

            self.raiz=tk.Toplevel(self.master)
            self.raiz.protocol("WM_DELETE_WINDOW", self.Cerrar)
            #self.raiz.focus_set()
            self.raiz.grab_set()
            self.raiz.title("TPI Inteligencia Artificial - Grupo 9")
            self.raiz.resizable(0,0)
            w=1280
            h=670
            ws = self.master.winfo_screenwidth()
            hs = self.master.winfo_screenheight()
            # calculate position x, y
            x = (ws/2) - (w/2)    
            y = (hs/2) - (h/2)
            self.raiz.geometry('%dx%d+%d+%d' % (w, h, x, y))
            # self.raiz.minsize(1280,670)
            # self.raiz.geometry("1200x690+70+20")
            self.raiz.config(bg="#9BBCD1")

            self.miFrame1=tk.Frame(self.raiz, width=800, height=100,bg="#9BBCD1",relief="groove", borderwidth=5)
            self.miFrame1.pack(fill="both",side="top")
            self.miFrame4=tk.Frame(self.raiz, width=800, height=600,bg="#9BBCD1",relief="groove", borderwidth=5)
            self.miFrame4.pack(fill="both",side="top",expand="YES")
            self.miFrame2=tk.Frame(self.miFrame4, width=800, height=100,bg="#9BBCD1")
            self.miFrame2.pack(fill="both",side="top",expand="YES")
            self.miFrame3=tk.Frame(self.miFrame4, width=800, height=410,bg="#9BBCD1")
            self.miFrame3.pack(fill="both",side="top",expand="YES")

            self.TituloMenu=tk.Label(self.miFrame1,bg="#9BBCD1", text="Generar Arboles de Decisión - Algoritmo C4.5",fg="#323638",font=("Ubuntu",25), anchor="center")
            self.TituloMenu.pack(fill="both",side="top")

            #Primer arbol
            Arbol = GenerarArbol(self.contenido)
            self.ArbolGain=Arbol.AlgoritmoC45(Arbol.tabla,Arbol.Atributes,[Arbol.Tree,Arbol.NodeParent])
            # write to a dot file
            Arbol.G.write('test.dot')

            #create a png file
            Arbol.G.layout(prog='dot') # use dot

            Arbol.G.draw('arbol.png')    

            #Segundo arbol
            Arbol = GenerarArbol(self.contenido)
            Arbol.TreexGan=False
            self.ArbolGainRatio=Arbol.AlgoritmoC45(Arbol.tabla,Arbol.Atributes,[Arbol.Tree,Arbol.NodeParent])
            # write to a dot file
            Arbol.G.write('test.dot')
            #create a png file
            Arbol.G.layout(prog='dot') # use dot
            Arbol.G.draw('arbol2.png') 

            self.graficar(0)

            self.click_btn= tk.PhotoImage(file='clip.png')

            #Let us create a label for button event

            #Let us create a dummy button and pass the image
            self.datoGain=IntVar()
            self.datoFile=tk.StringVar()
            self.datoFile.set(self.contenido)
            self.archivo = tk.Entry(self.miFrame2,textvariable=self.datoFile,bg="#9BBCD1",fg="green",state="readonly",width=60)
            self.archivo.place(x=50, y=65)
            self.button= tk.Button(self.miFrame2, image=self.click_btn,command= lambda:self.actualizarFile(self.datoFile,self.datoGain.get()),borderwidth=3,height = 40, width = 40)
            self.button.place(x=50, y=10)

            #Declaracion de RadiusButton para intercalar entre el grafico de Ganancia y Tasa de ganancia
            self.botonGan=Radiobutton(self.miFrame2,text="GANANCIA",variable=self.datoGain,value=0,bg="#9BBCD1",fg="black",pady=0,command=lambda:self.graficar(0))
            self.botonTas=Radiobutton(self.miFrame2,text="TASA DE GANANCIA",variable=self.datoGain,value=1,bg="#9BBCD1",fg="black",pady=0,command=lambda:self.graficar(1))
            self.botonGan.place(x=450, y=40)
            self.botonTas.place(x=450, y=60)   


            self.thresholdLabel=tk.Label(self.miFrame2,bg="#9BBCD1",text="Ingrese Threshold:",fg="black",height=2)
            self.datoTH=tk.StringVar()
            self.datoTH.set(0)
            self.entradaTH=tk.Entry(self.miFrame2,textvariable=self.datoTH)
            self.entradaTH.bind("<Return>", lambda x=None: self.actualizarTh( self.entradaTH.get(),self.datoGain.get() )  )
            self.thresholdLabel.place(x=650, y=30)
            self.entradaTH.place(x=650, y=60)

            self.pjelabel=tk.Label(self.miFrame2,bg="#9BBCD1",text="Porcentaje de Entrenamiento:",fg="black",height=2)
            self.pjelabel.place(x=800,y=50)
            self.porcentaje = tk.Scale(self.miFrame2, from_=1, to=100, orient=HORIZONTAL,length=250)
            self.porcentaje.set(100)
            self.porcentaje.bind("<ButtonRelease-1>", lambda x=None:self.actualizargrafico(self.datoGain.get()))
            self.porcentaje.place(x=980,y=40)

        else:   
            messagebox.showerror(message="Debe abrir un archivo .csv para continuar", title="ERROR")

    def updateValue(self,*args):
        print(self.porcentaje.get())

    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        if self.img.shape[1]>1280:
            if self.img.shape[0]>670:
                self.canvas.scan_dragto(event.x, event.y, gain=1)
            else:
                self.canvas.scan_dragto(event.x, 0, gain=1)
    # def actualizargrafico2(self,opc):

    def actualizargrafico(self,opc):
        #Primer arbol
        
        Arbol = GenerarArbol(self.contenido)
        Arbol.threshold = self.threshold
        # Arbol = GenerarArbol("./prueba5.csv")
        if self.porcentaje.get()!=100:
            pje= math.ceil(self.porcentaje.get()*(len(Arbol.tabla)-1)/100) + 1
            self.TablaTesteo=[]
            self.TablaTesteo.append(Arbol.tabla[0])
            TablaArbol=copy.deepcopy(Arbol.tabla)
            while len(TablaArbol)>pje:
                self.TablaTesteo.append(TablaArbol[-1])
                TablaArbol.pop(-1)
        print(TablaArbol,"AAAAAAAAAAAAAAAAAAAAAAAAAA")
        self.ArbolGain=Arbol.AlgoritmoC45(TablaArbol,Arbol.Atributes,[Arbol.Tree,Arbol.NodeParent])

        # write to a dot file
        Arbol.G.write('test.dot')

        #create a png file
        Arbol.G.layout(prog='dot') # use dot

        Arbol.G.draw('arbol.png')    

        #Segundo arbol
        Arbol = GenerarArbol(self.contenido)
        Arbol.threshold = self.threshold
        # Arbol = GenerarArbol("./prueba2.csv")
        Arbol.TreexGan=False
        self.ArbolGainRatio=Arbol.AlgoritmoC45(TablaArbol,Arbol.Atributes,[Arbol.Tree,Arbol.NodeParent])

        for t in self.ArbolGain:
            if not isinstance(t, str):
                print(t.getName())
                if t.getParent()!= None:
                    print(t.getParent().getName())
                print(t.getChild())
                for c in t.getChild():
                    print(c)

        # write to a dot file
        Arbol.G.write('test.dot')
        #create a png file
        Arbol.G.layout(prog='dot') # use dot
        Arbol.G.draw('arbol2.png') 

        self.graficar(opc)
        if opc ==0:
            if self.porcentaje.get()!=100:
                TT=copy.deepcopy(self.TablaTesteo)
                TT.pop(0)
                acertados=0
                for TablaTesteo in TT:
                    flag=True
                    print(self.TablaTesteo)
                    print(self.ArbolGain[0].getChild())
                    try:
                        nodeRaiz=self.ArbolGain[0].getChild()[TablaTesteo[self.TablaTesteo[0].index(self.ArbolGain[0].getName())]]
                        while flag and nodeRaiz.getChild() != {}:
                            try:
                                nodeRaiz=nodeRaiz.getChild()[TablaTesteo[self.TablaTesteo[0].index(nodeRaiz.getName())]]
                            except:
                                flag=False

                        if flag:
                            print(nodeRaiz.getName())
                            if nodeRaiz.getName()==TablaTesteo[-1]:
                                acertados+=1
                    except:
                            flag=False

                messagebox.showinfo(title="Punteria Ganancia", message="La punteria calculada con los datos de testeo es de %f %s" %( round(acertados*100/len(TT),1) , "%",))  
        else:
            if self.porcentaje.get()!=100:
                TT=copy.deepcopy(self.TablaTesteo)
                TT.pop(0)
                acertados=0
                for TablaTesteo in TT:
                    flag=True
                    print(self.TablaTesteo)
                    print(self.ArbolGainRatio[0].getChild())
                    try:
                        nodeRaiz=self.ArbolGainRatio[0].getChild()[TablaTesteo[self.TablaTesteo[0].index(self.ArbolGainRatio[0].getName())]]
                        while flag and nodeRaiz.getChild() != {}:
                            try:
                                nodeRaiz=nodeRaiz.getChild()[TablaTesteo[self.TablaTesteo[0].index(nodeRaiz.getName())]]
                            except:
                                flag=False

                        if flag:
                            print(nodeRaiz.getName())
                            if nodeRaiz.getName()==TablaTesteo[-1]:
                                acertados+=1
                    except:
                            flag=False

                messagebox.showinfo(title="Punteria Tasa de Ganancia", message="La punteria calculada con los datos de testeo es de %f %s" %( round(acertados*100/len(TT),1) , "%",))

        # if messagebox.askyesno(message="¿Desea agregar nuevas instancias?", title="Nuevas Instancias"):
        
        #     self.ObtenerInstancia(opc)
    
    def ObtenerInstancia(self,opc):
        self.NuevaInstancia=[]
        self.valorAtribute=self.TablaTesteo[0][0]
        self.win= Tk()

        #Define geometry of the window
        self.win.geometry("550x250")
        self.win.config(bg="#9BBCD1")

        miFrame1=tk.Frame(self.win, width=800, height=100,bg="#9BBCD1",relief="groove", borderwidth=5)
        miFrame1.pack(fill="both",side="top")

        self.value=tk.Label(miFrame1,bg="#9BBCD1",text="Ingrese el valor de %s:"%(self.valorAtribute),fg="black",height=2)
        datoV=tk.StringVar()
        datoV.set(0)
        entradaValue=tk.Entry(miFrame1,textvariable=datoV)
        self.botonValue=tk.Button(miFrame1, text="Agregar",bg="#2D373D",fg="#42D5FF",width=20,height=0,command=lambda:self.cambiarAtributo(entradaValue.get(),opc))

        self.value.pack(fill="both",side="top")
        entradaValue.pack(fill="both",side="top")
        self.botonValue.pack(fill="both",side="top")

        self.win.mainloop()

    def cambiarAtributo(self,valor,opc):
        self.NuevaInstancia.append(valor)
        if len(self.NuevaInstancia)==len(self.TablaTesteo[0]):
            if opc==0:
                try:
                    print(self.NuevaInstancia)
                    nodeRaiz=self.ArbolGain[0].getChild()[self.NuevaInstancia[self.TablaTesteo[0].index(self.ArbolGain[0].getName())]]
                    while flag and nodeRaiz.getChild() != {}:
                        try:
                            nodeRaiz=nodeRaiz.getChild()[self.NuevaInstancia[self.TablaTesteo[0].index(nodeRaiz.getName())]]
                        except:
                            flag=False

                    if flag:
                        messagebox.showinfo(title="Nueva instancia definida", message="La nueva instancia pertenece a la clase %s"%(nodeRaiz.getName(),))
                    else:
                        messagebox.showinfo(title="Nueva instancia definida", message="No se pudo clasificar la nueva instancia ingresada")
                except:
                    messagebox.showinfo(title="Nueva instancia definida", message="No se pudo clasificar la nueva instancia ingresada")   
            else:
                try:
                    print(self.NuevaInstancia)
                    nodeRaiz=self.ArbolGainRatio[0].getChild()[self.NuevaInstancia[self.TablaTesteo[0].index(self.ArbolGainRatio[0].getName())]]
                    while flag and nodeRaiz.getChild() != {}:
                        try:
                            nodeRaiz=nodeRaiz.getChild()[self.NuevaInstancia[self.TablaTesteo[0].index(nodeRaiz.getName())]]
                        except:
                            flag=False

                    if flag:
                        messagebox.showinfo(title="Nueva instancia definida", message="La nueva instancia pertenece a la clase %s"%(nodeRaiz.getName(),))
                    else:
                        messagebox.showinfo(title="Nueva instancia definida", message="No se pudo clasificar la nueva instancia ingresada")
                except:
                    messagebox.showinfo(title="Nueva instancia definida", message="No se pudo clasificar la nueva instancia ingresada")   
            self.win.destroy() 
            if messagebox.askyesno(message="¿Desea agregar nuevas instancias?", title="Nuevas Instancias"):
                self.ObtenerInstancia()     
        else:
            self.valorAtribute=self.TablaTesteo[0][self.TablaTesteo[0].index(self.valorAtribute)+1]
            self.value.pack_forget()
            self.value.pack(fill="both",side="top")
    
    def graficar(self,opc):
            
        if opc==0:
 

            self.img = cv2.imread('arbol.png')
            if self.img.shape[1] < 1280:
                x = (1280 - self.img.shape[1])/2
            else:
                x = 0
            self.canvas = tk.Canvas(self.miFrame3,width=1280,height=720,bg='#9BBCD1')

            self.xsb = tk.Scrollbar(self.miFrame3, orient="horizontal", command=self.canvas.xview)
            self.ysb = tk.Scrollbar(self.miFrame3, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
            self.canvas.configure(scrollregion=(-x,0,self.img.shape[1],self.img.shape[0]))

            self.xsb.grid(row=1, column=0, sticky="ew")
            self.ysb.grid(row=0, column=1, sticky="ns")
            self.canvas.grid(row=0, column=0, sticky="ne")
            self.miFrame3.grid_rowconfigure(0, weight=1)
            self.miFrame3.grid_columnconfigure(0, weight=1)

            # Escape / raw string literal
            one = tk.PhotoImage(file=r'arbol.png')
            self.master.one = one  # to prevent the image garbage collected.
            self.canvas.create_image(0,0, image=one, anchor='nw')
            
            self.canvas.bind("<ButtonPress-1>", self.scroll_start)
            self.canvas.bind("<B1-Motion>", self.scroll_move)
        else:

            self.img = cv2.imread('arbol2.png')

            if self.img.shape[1] < 1280:
                x = (1280 - self.img.shape[1])/2
            else:
                x = 0
            self.canvas = tk.Canvas(self.miFrame3,width=1280,height=720,bg='#9BBCD1')

            self.xsb = tk.Scrollbar(self.miFrame3, orient="horizontal", command=self.canvas.xview)
            self.ysb = tk.Scrollbar(self.miFrame3, orient="vertical", command=self.canvas.yview)
            self.canvas.configure(yscrollcommand=self.ysb.set, xscrollcommand=self.xsb.set)
            self.canvas.configure(scrollregion=(-x,0,self.img.shape[1],self.img.shape[0]))

            self.xsb.grid(row=1, column=0, sticky="ew")
            self.ysb.grid(row=0, column=1, sticky="ns")
            self.canvas.grid(row=0, column=0, sticky="n")
            self.miFrame3.grid_rowconfigure(0, weight=1)
            self.miFrame3.grid_columnconfigure(0, weight=1)

            # Escape / raw string literal
            one = tk.PhotoImage(file=r'arbol2.png')
            self.master.one = one  # to prevent the image garbage collected.
            self.canvas.create_image((0,0), image=one, anchor='nw')
            
            self.canvas.bind("<ButtonPress-1>", self.scroll_start)
            self.canvas.bind("<B1-Motion>", self.scroll_move)

if __name__ == "__main__":
    raizMaster = tk.Tk()
    Programa =  GraphicInterface(raizMaster,tk)
    raizMaster.mainloop()
    