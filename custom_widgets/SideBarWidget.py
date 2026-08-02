from PySide6.QtWidgets import QWidget, QStyleOption, QStyle
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtCore import Qt
class SideBarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Carrega a imagem uma única vez, na criação do widget, para não ficar a ler o arquivo do disco toda a vez que a tela repinta.
        self.pixmap = QPixmap("images/fundo-lateral.png")

    def paintEvent(self, event):
        # paintEvent é chamado pelo Qt toda a vez que o widget precisa de ser redesenhado (abrir a janela, redimensionar, mover, etc.)
        painter = QPainter(self)

        # Desenha o que o QSS definir. Widgets em Qt não aplicam QSS sozinhos quando você sobrescreve o paintEvent -, sendo preciso "pedir" manualmente para o estilo atual (o QSS carregado) desenhar o fundo/borda do widget aqui.
        option = QStyleOption()
        option.initFrom(self)
        self.style().drawPrimitive(QStyle.PrimitiveElement.PE_Widget, option, painter, self)

        # Desenha a imagem por cima, sem distorcer.
        if not self.pixmap.isNull(): # isNyll() = True se a imagem não carregou.
            # KeepAspectRationByExpanding = equivalente ao "background-size: cover" do CSS.
            # SmoothTransformation = usa suavização (bilinear) ao invés de pixelizar ao redimensionar.
            scaled = self.pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                Qt.TransformationMode.SmoothTransformation
            )

            # drawPixmap desenha a imagem na posição (-x, -y).
            # Como x/y são negativos (ou zero), a imagem "nasce" deslocada para fora dos limites do widget, e o Qt corta automaticamente tudo para passar da área visível.
            x = (scaled.width() - self.width()) / 2
            y = (scaled.height() - self.height()) / 2
            painter.drawPixmap(-int(x), -int(y), scaled)

        # Deixa o QWidget seguir o seu comportamento padrão depois (garante que outras coisas do clico de eventos do Qt não quebrem)
        super().paintEvent(event)