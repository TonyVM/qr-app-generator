import sys
import sqlite3
import qrcode
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QListWidget, QMessageBox

class MenuApp(QWidget):
    def __init__(self):
        super().__init__()

        # Lista para almacenar los platos del menú
        self.menu_items = []

        # Inicializar la conexión a la base de datos
        self.conn = sqlite3.connect('menu_database.db')
        self.cursor = self.conn.cursor()

        self.init_ui()

    def init_ui(self):
        # Crear elementos de la interfaz
        self.plato_label = QLabel('Plato:')
        self.plato_input = QLineEdit()
        self.precio_label = QLabel('Precio:')
        self.precio_input = QLineEdit()
        self.add_button = QPushButton('Agregar a Menú')
        self.eliminar_button = QPushButton('Eliminar Plato')
        self.menu_table = QTableWidget()
        self.qr_button = QPushButton('Generar QR')

        # Diseño principal
        layout = QVBoxLayout()

        # Fila 1: Plato y Precio
        fila_input_layout = QHBoxLayout()
        fila_input_layout.addWidget(self.plato_label)
        fila_input_layout.addWidget(self.plato_input)
        fila_input_layout.addWidget(self.precio_label)
        fila_input_layout.addWidget(self.precio_input)
        layout.addLayout(fila_input_layout)

        # Fila 2: Botones
        fila_botones_layout = QHBoxLayout()
        fila_botones_layout.addWidget(self.add_button)
        fila_botones_layout.addWidget(self.eliminar_button)
        layout.addLayout(fila_botones_layout)

        # Tabla y botón QR
        layout.addWidget(self.menu_table)
        layout.addWidget(self.qr_button)

        # Configurar la acción de los botones
        self.add_button.clicked.connect(self.agregar_plato)
        self.eliminar_button.clicked.connect(self.eliminar_plato)
        self.qr_button.clicked.connect(self.generar_qr)

        self.setLayout(layout)

        # Configuración de la ventana principal
        self.setWindowTitle('App de Menú con QR')
        self.setGeometry(300, 300, 600, 400)
        self.show()

        # Cargar datos de la base de datos al iniciar la aplicación
        self.cargar_base_de_datos()

    def agregar_plato(self):
        # Obtener el nombre y el precio del plato ingresado
        plato = self.plato_input.text().capitalize()
        precio = self.precio_input.text()

        # Verificar que se hayan ingresado ambos campos
        if not plato or not precio:
            QMessageBox.warning(self, 'Alerta', 'Por favor, ingresa el nombre y el precio del plato.')
            return

        # Verificar si el plato ya existe en la lista
        if any(p == plato for p, _ in self.menu_items):
            QMessageBox.warning(self, 'Alerta', 'Este plato ya existe en el menú.')
            return

        # Agregar el plato a la lista y a la base de datos
        self.menu_items.append((plato, precio))
        self.guardar_en_base_de_datos(plato, precio)
        self.actualizar_tabla()

        # Limpiar campos de entrada
        self.plato_input.clear()
        self.precio_input.clear()
        self.plato_input.setFocus()

    def eliminar_plato(self):
        # Obtener el ítem seleccionado en la tabla
        selected_row = self.menu_table.currentRow()

        if selected_row == -1:
            return

        # Obtener el plato desde la tabla
        plato = self.menu_table.item(selected_row, 0).text()

        # Eliminar el plato de la lista y de la base de datos
        self.menu_items = [(p, precio) for p, precio in self.menu_items if p != plato]
        self.eliminar_de_base_de_datos(plato)
        self.actualizar_tabla()

    def generar_qr(self):
        # Crear el mensaje del código QR con la lista de platos y precios
        mensaje = '\n'.join([f'{plato} - ${precio}' for plato, precio in self.menu_items])

        # Crear el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(mensaje)
        qr.make(fit=True)

        # Crear la imagen del código QR
        imagen_qr = qr.make_image(fill_color="black", back_color="white")

        # Guardar la imagen del código QR
        imagen_qr.save('menu_qr.png')

        # Mostrar mensaje de éxito
        QMessageBox.information(self, 'Éxito', 'Código QR generado con éxito. Guardado como menu_qr.png')

    def cargar_base_de_datos(self):
        try:
            # Crear la tabla si no existe
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS menu (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    plato TEXT NOT NULL,
                    precio REAL NOT NULL
                )
            ''')

            # Consultar platos y precios desde la base de datos
            self.cursor.execute('SELECT plato, precio FROM menu')
            rows = self.cursor.fetchall()

            # Actualizar la lista de platos
            self.menu_items = [(plato, precio) for plato, precio in rows]
            self.actualizar_tabla()

        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Error', f'Error al cargar la base de datos:\n{str(e)}')

    def guardar_en_base_de_datos(self, plato, precio):
        try:
            self.cursor.execute('INSERT INTO menu (plato, precio) VALUES (?, ?)', (plato, precio))
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Error', f'Error al guardar en la base de datos:\n{str(e)}')

    def eliminar_de_base_de_datos(self, plato):
        try:
            self.cursor.execute('DELETE FROM menu WHERE plato = ?', (plato,))
            self.conn.commit()
        except sqlite3.Error as e:
            QMessageBox.critical(self, 'Error', f'Error al eliminar de la base de datos:\n{str(e)}')

    def actualizar_tabla(self):
        # Limpiar la tabla actual
        self.menu_table.clear()
        self.menu_table.setRowCount(0)

        # Configurar la tabla
        self.menu_table.setColumnCount(2)
        self.menu_table.setHorizontalHeaderLabels(['Plato', 'Precio'])

        # Agregar elementos actualizados
        for row, (plato, precio) in enumerate(self.menu_items):
            self.menu_table.insertRow(row)
            self.menu_table.setItem(row, 0, QTableWidgetItem(str(plato)))
            self.menu_table.setItem(row, 1, QTableWidgetItem(str(precio)))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = MenuApp()
    sys.exit(app.exec_())
