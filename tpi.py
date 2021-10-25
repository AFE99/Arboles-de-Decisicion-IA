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
        self.NodeParent = {"parent":None,"branch":None}
        self.G=pgv.AGraph(directed=True)
        
        with open(path) as csvfile:
            reader = csv.reader(csvfile) # change contents to floats
            for row in reader: # each row is a list
                self.tabla.append(row)
        self.columnas=len(self.tabla[1])-1 #se le resta 1 para no incluir la columna de la clase

        self.Atributes = []

        for x in range(1,len(self.tabla[1])-1):
            self.Atributes.append(self.tabla[0][x])
        # print("Atributos: ",self.Atributes)

        print("------------------------------------------------TABLA-----------------------------------------------")
        self.prettyPrint(self.tabla)
        print("----------------------------------------------------------------------------------------------------")

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

            for Dj in entropysAtr[e]["Djs"]: #Calcula la tasa de ganancia para el atributo "e" del ciclo for
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
        
        if self.TreexGan:
            return NodoG
        else: 
            return NodoTG

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
            Tree[0].append(self.NodeSheet)
            self.G.add_node("Nodo%i"%len(Tree[0]),label=self.NodeSheet, color='green')
            self.G.add_edge(Tree[1]["parent"],"Nodo%i"%len(Tree[0]), color='black',label=Tree[1]["branch"])
            # Tree[0].append(Node(self.NodeSheet,Tree[1]["parent"]))
            # Tree[1].setChild[Tree[0][len(Tree[0])-1],Tree[1]["branch"]]
        elif len(Atributes) == 0:
            print("No hay mas atributos a analizar, tabla= ", pprint(Tabla, width=1))
            # print(Tabla)

            Tree[0].append(self.ValorMasFreq(Tabla))
            self.G.add_node("Nodo%i"%len(Tree[0]),label=self.ValorMasFreq(Tabla), color='green')
            self.G.add_edge(Tree[1]["parent"],"Nodo%i"%len(Tree[0]), color='black',label=Tree[1]["branch"])
            # for x in Tree[0]:
            #     print(x.getName())
            #     print(x.getChild())
            #     print(x.getParent())
        else:
            pg= self.calcEntropy(self.varConjD(Tabla)) #Se almacena la entropia del conjunto D

            EntropysAtr = self.calcEntropyAtr(Tabla,Atributes)
            # print(EntropysAtr)
            Ag = self.mejorGananciayTasa(pg,EntropysAtr,Tabla)

            if False:
                print("threshold section")
            else:
                NodeParent = copy.deepcopy(Tree[1])

                #Tree[0].append(Node(Ag,NodeParent["parent"]))
                Tree[0].append(Ag)
                
                if NodeParent["parent"]== None:
                    self.G.add_node(Ag, color='red')
                    NodeParent["parent"] = Ag
                else:
                    self.G.add_node("Nodo%i"%len(Tree[0]),label=Ag, color='blue')
                    self.G.add_edge(NodeParent["parent"],"Nodo%i"%len(Tree[0]), color='black',label=NodeParent["branch"])

                    NodeParent["parent"] = "Nodo%i"%len(Tree[0])

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

                Atributes2 = copy.deepcopy(Atributes)
                Atributes2.remove(Ag)

                for Dj in range(len(Dpartition)):
                    Tree[0].append(EntropysAtr[Ag]["Vars"][Dj])
                    NodeParent["branch"] = EntropysAtr[Ag]["Vars"][Dj]
                    # print(NodeParent["branch"])
                    # input()
                    # Tree[0][len(Tree[0])-1].setChild(None,EntropysAtr[Ag]["Vars"][Dj])

                    Tabla = Dpartition[Dj]
                    # print("ENTREEE")
                    self.AlgoritmoC45(Tabla,Atributes2,[Tree[0],NodeParent])

        print("\nArbol: ",Tree[0])
        print("\n Los atributos identificados son: ",Atributes,len(Atributes))

class GraphicInterface:
    def __init__(self, master,tk):
        self.contenido=None #Variable que guardará la ruta del archivo a abrir
        self.master = master
        self.agregar_menu()
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
        # opciones1.add_command(label="Abrir archivo", command=self.abrirAr)
        menubar1.add_cascade(label="Abrir Archivo", command=self.abrirAr)

    def abrirAr(self):
        print("asdas")
        nombrearch=fd.askopenfilename(initialdir = os.path.abspath(os.getcwd()),title = "Seleccione archivo",filetypes = (("Archivos CSV","*.csv"),("Todos los archivos","*.*")))
        if nombrearch!='':
            self.contenido=nombrearch

    def actualizarFile(self,archivo,opc):
        fileant = self.contenido
        self.abrirAr()
        archivo["text"] = self.contenido
        if fileant != self.contenido:
            self.actualizargrafico(opc)

    def MenuPrincipal(self):
        if self.contenido!=None:
            self.raiz=tk.Toplevel(self.master)
            #self.raiz.focus_set()
            #self.raiz.grab_set()
            self.raiz.title("TPI Inteligencia Artificial - Grupo 9")
            #self.raiz.resizable(0,0)
            w=1280
            h=670
            ws = self.master.winfo_screenwidth()
            hs = self.master.winfo_screenheight()
            # calculate position x, y
            x = (ws/2) - (w/2)    
            y = (hs/2) - (h/2)
            self.raiz.geometry('%dx%d+%d+%d' % (w, h, x, y))
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
            # Arbol = GenerarArbol("./prueba5.csv")
            Arbol.AlgoritmoC45(Arbol.tabla,Arbol.Atributes,[Arbol.Tree,Arbol.NodeParent])
            # write to a dot file
            Arbol.G.write('test.dot')

            #create a png file
            Arbol.G.layout(prog='dot') # use dot

            Arbol.G.draw('arbol.png')    

            #Segundo arbol
            Arbol = GenerarArbol(self.contenido)
            # Arbol = GenerarArbol("./prueba2.csv")
            Arbol.TreexGan=False
            Arbol.AlgoritmoC45(Arbol.tabla,Arbol.Atributes,[Arbol.Tree,Arbol.NodeParent])
            # write to a dot file
            Arbol.G.write('test.dot')
            #create a png file
            Arbol.G.layout(prog='dot') # use dot
            Arbol.G.draw('arbol2.png') 

            self.graficar(0)

            self.click_btn= tk.PhotoImage(file='clip.png')

            #Let us create a label for button event

            #Let us create a dummy button and pass the image
            self.datoTLl=IntVar()
            self.archivo = tk.Label(self.miFrame2,bg="#9BBCD1",text=self.contenido,fg="green",height=2)
            self.archivo.place(x=120, y=65)
            self.button= tk.Button(self.miFrame2, image=self.click_btn,command= lambda:self.actualizarFile(self.archivo,self.datoTLl),borderwidth=3,height = 40, width = 40)
            self.button.place(x=120, y=10)

            #Declaracion de RadiusButton para intercalar entre el grafico de Ganancia y Tasa de ganancia
            self.botonGan=Radiobutton(self.miFrame2,text="GANANCIA",variable=self.datoTLl,value=0,bg="#9BBCD1",fg="black",pady=0,command=lambda:self.graficar(0))
            self.botonTas=Radiobutton(self.miFrame2,text="TASA DE GANANCIA",variable=self.datoTLl,value=1,bg="#9BBCD1",fg="black",pady=0,command=lambda:self.graficar(1))
            self.botonGan.place(x=520, y=40)
            self.botonTas.place(x=520, y=60)   


            self.threshold=tk.Label(self.miFrame2,bg="#9BBCD1",text="Ingrese Threshold:",fg="black",height=2)
            self.datoTH=tk.StringVar()
            self.entradaTH=tk.Entry(self.miFrame2,textvariable=self.datoTH)
            # self.entradaTH.bind("<Return>", self.graficar)
            self.threshold.place(x=820, y=40)
            self.entradaTH.place(x=950, y=45)

        else:   
            messagebox.showerror(message="Debe abrir un archivo .csv para continuar", title="ERROR")

        
        
            # Arbol = GenerarArbol("./prueba.csv")
            
        


       
        # #canvas.get_tk_widget().grid(row=0,column=0,pady=5)

        # self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.raiz)
        # self.toolbar2.update()
        #toolbar2.pack(side="bottom",anchor=W)
        # self.canvas2.get_tk_widget().place(x=530,y=150)
       
        # self.toolbar2.place(x=612,y=634)

        #fig2.add_subplot(111).axis("equal")
        # plt.figure(figsize=(20,15),dpi=40)
        # image = Image.open('arbol.png')
        # plt.axis('off')
        # plt.imshow(image,aspect="auto")
        # plt.show()
    def scroll_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def scroll_move(self, event):
        if self.img.shape[1]>1280:
            if self.img.shape[0]>670:
                self.canvas.scan_dragto(event.x, event.y, gain=1)
            else:
                self.canvas.scan_dragto(event.x, 0, gain=1)

    def actualizargrafico(self,opc):
        #Primer arbol
        Arbol = GenerarArbol(self.contenido)
        # Arbol = GenerarArbol("./prueba5.csv")
        Arbol.AlgoritmoC45(Arbol.tabla,Arbol.Atributes,[Arbol.Tree,Arbol.NodeParent])
        # write to a dot file
        Arbol.G.write('test.dot')

        #create a png file
        Arbol.G.layout(prog='dot') # use dot

        Arbol.G.draw('arbol.png')    

        #Segundo arbol
        Arbol = GenerarArbol(self.contenido)
        # Arbol = GenerarArbol("./prueba2.csv")
        Arbol.TreexGan=False
        Arbol.AlgoritmoC45(Arbol.tabla,Arbol.Atributes,[Arbol.Tree,Arbol.NodeParent])
        # write to a dot file
        Arbol.G.write('test.dot')
        #create a png file
        Arbol.G.layout(prog='dot') # use dot
        Arbol.G.draw('arbol2.png') 

        self.graficar(opc)

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
            print(one)
            self.master.one = one  # to prevent the image garbage collected.
            self.canvas.create_image((0,0), image=one, anchor='nw')
            
            self.canvas.bind("<ButtonPress-1>", self.scroll_start)
            self.canvas.bind("<B1-Motion>", self.scroll_move)
        # if opc==0:
        #     image = Image.open('arbol.png')
        #     self.fig = Figure(figsize=(28, 10), dpi=53)
        #     self.ax = self.fig.add_subplot(111)
        #     self.ax.text(0.0,-5.0,"Arbol de Decisión segun Ganancia", fontsize=15)
        #     self.ax.axis('off')
        #     # self.fig.axis('off')
        #     self.ax.imshow(image)
        #     # self.ax.axis([0,500,0,500])
        #     #self.fig.add_subplot(111).plot([], [], marker = 'o')
        #     self.fig.set_facecolor('#9BBCD1')
        #     self.canvas = FigureCanvasTkAgg(self.fig, master=self.raiz)  # A tk.DrawingArea.
        #     self.canvas.draw()
        #     self.toolbar = NavigationToolbar2Tk(self.canvas, self.raiz)
        #     self.canvas.get_tk_widget().place(relx=0.5, rely=0.6, anchor=CENTER)
        # else:
        #     image2 = Image.open('arbol2.png')
        #     self.fig2 = Figure(figsize=(28,10), dpi=53)
        #     self.ax2 = self.fig2.gca()
        #     self.ax2.text(0.0,-5.0,"Arbol de Decisión segun Tasa Ganancia", fontsize=15)
        #     self.ax2.axis('off')
        #     # self.fig.axis('off')
        #     self.ax2.imshow(image2)
        #     #self.fig2.add_subplot(111).plot([], [], marker = 'o')
        #     self.fig2.set_facecolor('#9BBCD1')
        #     self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.raiz)  # A tk.DrawingArea.
        #     self.canvas2.draw()
        #     self.toolbar = NavigationToolbar2Tk(self.canvas2, self.raiz)
        #     self.canvas2.get_tk_widget().place(relx=0.5, rely=0.6, anchor=CENTER)
        # self.toolbar.update()
        # self.toolbar.place(x=3,y=675)

if __name__ == "__main__":
    raizMaster = tk.Tk()
    Programa =  GraphicInterface(raizMaster,tk)
    raizMaster.mainloop()
    