# imports auxiliares
import sys
import requests
from datetime import date, timedelta
import concurrent.futures

# imports pyqt5
from PyQt5.QtWidgets import *
# Permite acesso a variaveis importantes
from PyQt5 import QtCore
from PyQt5.QtGui import QCursor
# Permite leitura do arquivo .ui
from PyQt5 import uic
# Permite plotar graficos
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

moedas_dict = requests.get('https://economia.awesomeapi.com.br/json/all').json()
threads = list()

class MyWindow(QMainWindow):

    def __init__(self):
        super(MyWindow, self).__init__()
        # uic.loadUi(r'C:\Users\diogo\dev\Projects\python\coin_tracker_PyQt5\Teste.ui', self)
        uic.loadUi(r'Teste.ui', self)
        self.show()
        # Adicionando Opcoes na Droplist (Combobox)
        self.in_lista_cot.addItems([' '] + list(moedas_dict.keys()))

        # Interacoes
        self.in_lista_cot.currentTextChanged.connect(self._cot_btn)
        self.in_botao_cot.clicked.connect(self._get_cot)
        self.in_plot.clicked.connect(self._plot)
        self.in_quit.clicked.connect(self._quit_app)

        # Settando hoje como padrao
        self.in_data_cot.setDateTime(QtCore.QDateTime.currentDateTime())

        # Adicionando Layout horizontal pro frame do grafico
        self.layout_horizontal = QHBoxLayout(self.fix_frame_3)
        self.layout_horizontal.setObjectName('layout_horizontal')

        # Criando Grafico em Branco
        self.figure = plt.figure(figsize=(1, 1))
        self.canvas = FigureCanvas(self.figure)

        # Adicionando grafico em branco ao layout do frame
        self.layout_horizontal.addWidget(self.canvas)

    def _cot_btn(self):
        if self.in_lista_cot.currentText() == ' ':
            self.in_botao_cot.setEnabled(False)
            self.in_data_cot.setEnabled(False)
            self.in_plot.setEnabled(False)
        else:
            self.in_botao_cot.setEnabled(True)
            self.in_data_cot.setEnabled(True)
            self.in_plot.setEnabled(True)

    def _get_cot(self):
        dia, mes, ano = tuple(self.in_data_cot.dateTime().toString('dd MM yyyy').split())
        moeda = self.in_lista_cot.currentText()
        link = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/?start_date={ano+mes+dia}&end_date={ano+mes+dia}'
        request = requests.get(link)
        if request.json():
            info = request.json()[0]
            moeda_target = info['name'].split('/')[0]
            cotacao = info['bid']
            out = f'Cotacao {moeda_target}: R${cotacao}'
            self.out_resposta.setText(out)
        else:
            self.out_resposta.setText('Cotação indisponível')

    def _plot(self):
        QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)

        dia, mes, ano = tuple(self.in_data_cot.dateTime().toString('dd MM yyyy').split())
        self.figure.clear()
        x = list()
        y = list()
        data = date(int(ano), int(mes), int(dia)) - timedelta(days=170)

        # Requests em Threads diferentes
        with concurrent.futures.ThreadPoolExecutor() as executor:
            target_dates = [data + timedelta(days=(i*10)) for i in range(18)]
            results = executor.map(self._get_cotacao_parcial, target_dates)
            for result, data in zip(results, target_dates):
                f_result = float(result)
                x.append(f'{data.day:02}/{data.month}')
                y.append(f_result)

        for dia, cotacao in zip(x, y):
            if cotacao == -1:
                x.remove(dia)
                y.remove(cotacao)

        plt.plot(x, y, label=self.in_lista_cot.currentText())
        plt.legend(loc='lower right')
        plt.title('Projeção ultimos 6 meses')
        plt.ylabel('Cotaçao (R$)')
        plt.ylim((0, (max(y)*1.1)))
        plt.grid(True)
        self.canvas.draw()
        QApplication.restoreOverrideCursor()

    def _quit_app(self):
        sys.exit()

    def _get_cotacao_parcial(self, data):
        dia = data.day
        mes = data.month
        ano = data.year
        moeda = self.in_lista_cot.currentText()
        link = f'https://economia.awesomeapi.com.br/json/daily/{moeda}-BRL/?start_date={ano:04}{mes:02}{dia:02}&end_date={ano:04}{mes:02}{dia:02}'
        print(link)
        request = requests.get(link)
        if request.json():
            info = request.json()[0]
            y = info['bid']
        else:
            y = -1
        return y

def main():
    app = QApplication([])
    window = MyWindow()
    app.exec_()

if __name__ == "__main__":
    main()
