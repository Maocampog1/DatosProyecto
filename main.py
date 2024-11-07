import sys
import random
import numpy as np
from PyQt5 import QtWidgets, QtGui, QtCore
from grafos_ui import Ui_MainWindow
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsTextItem, QGraphicsItem


class Nodo(QGraphicsEllipseItem):
    def __init__(self, x, y, radius, id, app):
        super().__init__(-radius, -radius, 2 * radius, 2 * radius)
        self.setBrush(QtGui.QBrush(QtGui.QColor("lightblue")))
        self.setPen(QtGui.QPen(QtCore.Qt.black))
        self.id = id
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setFlag(QGraphicsEllipseItem.ItemSendsGeometryChanges)
        self.text_item = QGraphicsTextItem(f"Nodo {self.id}", self)
        self.text_item.setPos(-10, -10)
        self.app = app
        self.aristas = []

    def agregar_arista(self, arista):
        self.aristas.append(arista)

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            for arista in self.aristas:
                arista.actualizar_posiciones()
        return super().itemChange(change, value)


class Arista(QGraphicsLineItem):
    def __init__(self, nodo1, nodo2, peso, scene):
        super().__init__()
        self.nodo1 = nodo1
        self.nodo2 = nodo2
        self.peso = peso
        self.scene = scene

        self.text_item = QGraphicsTextItem(str(self.peso))
        self.scene.addItem(self.text_item)

        self.actualizar_posiciones()

        self.setFlag(QGraphicsLineItem.ItemIsSelectable)
        self.setPen(QtGui.QPen(QtCore.Qt.black))

    def actualizar_posiciones(self):
        x1, y1 = self.nodo1.scenePos().x(), self.nodo1.scenePos().y()
        x2, y2 = self.nodo2.scenePos().x(), self.nodo2.scenePos().y()

        self.setLine(x1, y1, x2, y2)
        self.text_item.setPos((x1 + x2) / 2, (y1 + y2) / 2)

    def mousePressEvent(self, event):
        self.setPen(QtGui.QPen(QtCore.Qt.red, 3))
        self.nodo1.setPen(QtGui.QPen(QtCore.Qt.red, 3))
        self.nodo2.setPen(QtGui.QPen(QtCore.Qt.red, 3))
        super().mousePressEvent(event)


class GrafoApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(GrafoApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.graphicsView = self.ui.graphicsView
        self.scene = QGraphicsScene()
        self.graphicsView.setScene(self.scene)

        # Conectar los botones
        self.ui.btnPintarGrafo.clicked.connect(self.dibujar_grafo)
        self.ui.tableWidget.horizontalHeader().sectionClicked.connect(self.llenar_matriz_aleatoria)
        self.ui.btntablaAdyasencia.clicked.connect(self.generar_matriz_adyacencia)
        self.ui.btntablak2.clicked.connect(lambda: self.calcular_potencia_matriz(2))
        self.ui.btntablak3.clicked.connect(lambda: self.calcular_potencia_matriz(3))

        self.nodos = []
        self.aristas = []

    def dibujar_grafo(self):
        try:
            self.scene.clear()
            self.nodos.clear()
            self.aristas.clear()

            matriz = self.obtener_matriz()
            self.dibujar_nodos_y_aristas(matriz)
        except Exception as e:
            print(f"Error al dibujar el grafo: {e}")

    def obtener_matriz(self):
        try:
            filas = self.ui.tableWidget.rowCount()
            columnas = self.ui.tableWidget.columnCount()
            matriz = []
            for i in range(filas):
                fila = []
                for j in range(columnas):
                    item = self.ui.tableWidget.item(i, j)
                    valor = int(item.text()) if item and item.text().isdigit() else 0
                    fila.append(valor)
                matriz.append(fila)
            return matriz
        except Exception as e:
            print(f"Error al obtener la matriz: {e}")
            return []

    def dibujar_nodos_y_aristas(self, matriz):
        try:
            num_nodos = len(matriz)
            radius = 20
            width = self.graphicsView.width() - 100
            height = self.graphicsView.height() - 100

            for i in range(num_nodos):
                x = random.randint(50, width)
                y = random.randint(50, height)
                nodo = Nodo(x, y, radius, i + 1, self)
                nodo.setPos(x, y)
                self.scene.addItem(nodo)
                self.nodos.append(nodo)

            for i in range(num_nodos):
                for j in range(i + 1, num_nodos):
                    peso = matriz[i][j]
                    if peso > 0:
                        nodo1 = self.nodos[i]
                        nodo2 = self.nodos[j]
                        arista = Arista(nodo1, nodo2, peso, self.scene)
                        self.aristas.append(arista)
                        self.scene.addItem(arista)
                        nodo1.agregar_arista(arista)
                        nodo2.agregar_arista(arista)
        except Exception as e:
            print(f"Error al dibujar nodos y aristas: {e}")

    def llenar_matriz_aleatoria(self, index):
        """Llena la matriz de pesos con conexiones aleatorias, asegurando que todos los nodos tengan al menos una conexión."""
        try:
            filas = self.ui.tableWidget.rowCount()
            columnas = self.ui.tableWidget.columnCount()

            probabilidad_conexion = 0.5  # Ajusta la probabilidad de conexión (50% en este caso)

            for i in range(filas):
                for j in range(columnas):
                    if i == j:
                        self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem('0'))
                    else:
                        # Determina si debe haber conexión entre los nodos i y j
                        if random.random() < probabilidad_conexion:
                            valor_aleatorio = random.randint(1, 100)
                            self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(valor_aleatorio)))
                        else:
                            self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem('0'))

            # Asegurarse de que cada nodo tenga al menos una conexión
            for i in range(filas):
                conexiones = sum(1 for j in range(columnas) if self.ui.tableWidget.item(i, j) and int(self.ui.tableWidget.item(i, j).text()) > 0)
                
                # Si el nodo `i` no tiene conexiones, fuerza una conexión aleatoria
                if conexiones == 0:
                    j = random.choice([x for x in range(columnas) if x != i])
                    valor_aleatorio = random.randint(1, 100)
                    self.ui.tableWidget.setItem(i, j, QtWidgets.QTableWidgetItem(str(valor_aleatorio)))
                    # Hacer la conexión bidireccional
                    self.ui.tableWidget.setItem(j, i, QtWidgets.QTableWidgetItem(str(valor_aleatorio)))

        except Exception as e:
            print(f"Error al llenar la matriz: {e}")

    def generar_matriz_adyacencia(self):
        matriz_pesos = self.obtener_matriz()
        matriz_adyacencia = [[1 if valor > 0 else 0 for valor in fila] for fila in matriz_pesos]
        self.mostrar_en_tabla(self.ui.tablaAdyasencia, matriz_adyacencia)

    def calcular_potencia_matriz(self, k):
        matriz_adyacencia = np.array(self.obtener_matriz_adyacencia())
        matriz_k = np.linalg.matrix_power(matriz_adyacencia, k)
        if k == 2:
            self.mostrar_en_tabla(self.ui.tablak2, matriz_k.tolist())
        elif k == 3:
            self.mostrar_en_tabla(self.ui.tablak3, matriz_k.tolist())

    def obtener_matriz_adyacencia(self):
        matriz_pesos = self.obtener_matriz()
        return [[1 if valor > 0 else 0 for valor in fila] for fila in matriz_pesos]

    def mostrar_en_tabla(self, tabla, matriz):
        tabla.setRowCount(len(matriz))
        tabla.setColumnCount(len(matriz[0]))
        for i in range(len(matriz)):
            for j in range(len(matriz[i])):
                tabla.setItem(i, j, QtWidgets.QTableWidgetItem(str(matriz[i][j])))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GrafoApp()
    window.show()
    sys.exit(app.exec_())
