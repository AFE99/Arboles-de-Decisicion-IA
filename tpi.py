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

#Recorre ultima fila, salteando el encabezado de la misma
list=[]
for i in range(1,len(tabla)-1):
    if ([tabla[i][len(tabla[1])-1],0]) in list:
        #TERMINAR/ARREGLAR - Aca estoy intentando guardar la sumatoria de 'SI's y 'NO's de la ultima columna
        for k in range(1,len(tabla)-1):
            if 'a'=='a':
                list[k]='PROBANDO'
                print('PROBANDO')

    else:
        list.append([(tabla[i][len(tabla[1])-1]),0])
print(list)