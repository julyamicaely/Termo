import random
from urllib.error import URLError, HTTPError
from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.core.text import LabelBase
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from urllib.request import urlopen
from kivy.clock import Clock

Window.size = (360, 640)
LabelBase.register(name='Anton', fn_regular='assets/fonts/Anton-Regular.ttf')
LabelBase.register(name='Lexi', fn_regular='assets/fonts/LexendGiga-ExtraBold.ttf')


class TermoApp(MDApp):
    cores = {'verde': (0, .35, 0, 1), 'amarelo': (.45, .45, 0, 1), 'vermelho': (.40, 0, 0, 1), 'branco': (1, 1, 1, 1),
             'azulescuro': (0, 0, .35, 1), 'azulfoco': (0, 0, .6, 1), 'fundo': (0, 0, 0.17, 1)}

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.aviso = None
        self.espacos = []
        self.palavras = []
        self.palavrasecreta = ''
        self.dicausada = False
        self.tentativas = 0

    def build(self):
        self.theme_cls.theme_style = "Dark"
        Window.bind(on_key_down=self.clique)
        self.carregapalavras()
        self.criacampos()
        self.criateclado()

    def carregapalavras(self):  # carrega a lista de palavras de um link online
        link = 'https://www.ime.usp.br/~pf/dicios/br-sem-acentos.txt'
        reserva = 'assets/reserva.txt'
        try:
            abrelink = urlopen(link)
            tudojunto = abrelink.read()
        except (URLError, HTTPError, TimeoutError, ConnectionResetError):  # e se não conseguir vai pro arquivo local
            with open(reserva, 'rb') as txt:
                tudojunto = txt.read()

        separado = tudojunto.splitlines()   # separa as palavras em linhas
        for c in separado:
            if len(c) == 5:          # pega as palavras que têm 5 letras
                self.palavras.append(c.decode('utf-8').upper())
        self.palavrasecreta = random.choice(self.palavras).upper()  # sorteia uma delas
        print(self.palavrasecreta)

    def criacampos(self):  # cria 30 campos de texto (6 linhas e 5 colunas) para as letras
        casas = self.root.ids.casas
        for i in range(30):
            cada = MDTextField(mode='fill', size_hint_x=None, width=70, font_name='Lexi',
                               text_color_normal=self.cores['branco'], text_color_focus=self.cores['branco'],
                               font_size=18, fill_color_normal=self.cores['azulescuro'],
                               fill_color_focus=self.cores['azulfoco'], multiline=False)
            self.espacos.append(cada)
            cada.bind(text=self.limite)
            casas.add_widget(cada)

    def criateclado(self):  # cria teclado com as letras os botões enter e apagar
        teclado = self.root.ids.teclado
        for c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            tecla = MDFlatButton(text=c, font_name='Lexi', font_size=18, theme_text_color='Custom',
                                 text_color=self.cores['branco'], md_bg_color=self.cores['azulescuro'])
            tecla.bind(on_press=self.adiciona)
            teclado.add_widget(tecla)
        enter = MDFlatButton(text='ENTER', font_name='Lexi', font_size=16, md_bg_color=self.cores['azulescuro'],
                             theme_text_color='Custom', text_color=self.cores['branco'])
        enter.bind(on_press=self.avalia)
        apagar = MDFlatButton(text='APAGAR', font_name='Lexi', font_size=16, md_bg_color=self.cores['azulescuro'],
                              theme_text_color='Custom', text_color=self.cores['branco'])
        apagar.bind(on_press=self.deleta)
        teclado.add_widget(enter)
        teclado.add_widget(apagar)

    def clique(self, _window, key, _scancode, _codepoint, _modifiers):
        if key == 13:      # liga as teclas enter e backspace as mesmas funções que os botões do teclado
            self.avalia(None)
        elif key == 8:
            self.deleta(None)

    def limite(self, campo, texto):  # limita o campo a uma letra e passa o foco pro proximo campo
        if len(texto) > 1:
            campo.text = texto[:1].upper()
        elif len(texto) == 1:
            campo.text = texto.upper()
            self.proximo(campo)

    def proximo(self, campo):   # move o foco para o proximo campo desde que ele esteja na mesma linha
        indice = self.espacos.index(campo)
        if (indice + 1) % 5 != 0:
            self.espacos[indice + 1].focus = True

    def adiciona(self, botao):  # adiciona letra do teclado virtual no primeiro campo em branco
        texto = botao.text
        for campo in self.espacos:
            if not campo.text:
                campo.text = texto
                self.proximo(campo)
                break

    def deleta(self, _args):  # apaga a ultima letra digitada
        for campo in reversed(self.espacos):
            if campo.disabled:
                continue
            if campo.text:
                campo.text = ''
                campo.focus = True
                break

    def avalia(self, _args):
        linhatual = self.tentativas
        linha = self.espacos[linhatual * 5: (linhatual + 1) * 5]
        chute = ''.join(c.text for c in linha).upper()
        acertou = False

        if len(chute) == 5 and chute in self.palavras:
            contador = {}
            for letra in self.palavrasecreta:
                contador[letra] = contador.get(letra, 0) + 1

            # Primeira passada: letras verdes
            for pos in range(5):
                letra_chute = chute[pos]
                if letra_chute == self.palavrasecreta[pos]:
                    linha[pos].fill_color_normal = self.cores['verde']
                    self.cordatecla(letra_chute, self.cores['verde'])
                    contador[letra_chute] -= 1
                    # Atualiza o foco para renderizar a cor verde
                    Clock.schedule_once(lambda dt, campo=linha[pos]: setattr(campo, 'focus', True), 0.1)

            # Segunda passada: letras amarelas/vermelhas
            for pos in range(5):
                letra_chute = chute[pos]
                if letra_chute != self.palavrasecreta[pos]:  # Ignora as verdes
                    if letra_chute in contador and contador[letra_chute] > 0:
                        linha[pos].fill_color_normal = self.cores['amarelo']
                        self.cordatecla(letra_chute, self.cores['amarelo'])
                        contador[letra_chute] -= 1
                    else:
                        linha[pos].fill_color_normal = self.cores['vermelho']
                        self.cordatecla(letra_chute, self.cores['vermelho'])

                    # Atualiza o foco para renderizar as cores amarelo/vermelho
                    Clock.schedule_once(lambda dt, campo=linha[pos]: setattr(campo, 'focus', True), 0.1)

            if chute == self.palavrasecreta:
                self.popup('Parabéns, você acertou!')
                acertou = True
            else:
                self.tentativas += 1

            if self.tentativas > 5 and not acertou:
                self.popup(f'Você perdeu, a palavra era {self.palavrasecreta}')

            for c in linha:
                c.disabled = True

    def dica(self):  # destaca 3 letras que não estão na palavra e que ainda não foram escritas
        if self.dicausada:
            return
        self.dicausada = True
        bdica = self.root.ids.botaodica
        bdica.icon = 'lightbulb-outline'
        escritas = [le.text for le in self.espacos if le.text]
        erradas = [le for le in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' if le not in self.palavrasecreta and le not in escritas]
        erradasdica = random.sample(erradas, 3)
        for b in self.root.ids.teclado.children:
            if hasattr(b, 'text') and len(b.text) == 1 and b.text in erradasdica:
                b.md_bg_color = self.cores['vermelho']

    def reinicia(self):   # reseta tudo para reiniciar o jogo
        self.palavrasecreta = random.choice(self.palavras).upper()
        print(self.palavrasecreta)
        for campo in self.espacos:
            campo.disabled = False
            campo.text = ''
            campo.fill_color_normal = self.cores['azulescuro']
            campo.fill_color_focus = self.cores['azulfoco']
        for b in self.root.ids.teclado.children:
            if hasattr(b, 'text') and len(b.text) == 1:
                b.md_bg_color = self.cores['azulescuro']
        self.dicausada = False
        bdica = self.root.ids.botaodica
        bdica.icon = 'lightbulb-on'
        self.tentativas = 0
        if self.aviso:
            self.aviso.dismiss()
            self.aviso = None

    def cordatecla(self, letra, cor):  # muda a cor da tecla igual a do campo de texto
        for b in self.root.ids.teclado.children:
            if hasattr(b, 'text') and b.text == letra:
                b.md_bg_color = cor

    def popup(self, resultado):  # mostra resultado se ganhou ou perdeu
        if not self.aviso:
            self.aviso = MDDialog(title=f'{resultado}', md_bg_color=self.cores['azulfoco'],
                                  buttons=[MDFlatButton(text='Reiniciar',
                                                        on_release=self.reiniciapopup),
                                           MDFlatButton(text='Sair',
                                                        on_release=self.stop)])  # fecha o jogo
        self.aviso.open()

    def reiniciapopup(self, _args):  # fecha o popup e reinicia o jogo
        self.aviso.dismiss()
        self.reinicia()


if __name__ == '__main__':
    TermoApp().run()
