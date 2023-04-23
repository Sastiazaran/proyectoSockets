import pygame as pg

def get_font(size): # Returns Press-Start-2P in the desired size
    return pg.font.Font("./client/resources/font.ttf", size)

class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pg.Rect(x, y, width, height)
        self.color = (255, 255, 255)
        self.text = text
        self.font = get_font(30)
        self.txt_surface = self.font.render(text, True, self.color)
        self.active = False

    

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            
            # Si el usuario hace clic en la caja de entrada de texto, activa la caja de entrada de texto
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            # Cambia el color de la caja de entrada de texto si está activa
            self.color = (255, 255, 255) if self.active else (128, 128, 128)

        if event.type == pg.KEYDOWN:
            if self.active:
                if event.key == pg.K_RETURN:
                    # Si el usuario presiona enter, desactiva la caja de entrada de texto
                    self.active = False
                elif event.key == pg.K_BACKSPACE:
                    # Si el usuario presiona backspace, borra el último caracter de la caja de entrada de texto
                    self.text = self.text[:-1]
                else:
                    # Agrega cualquier otro caracter ingresado por el usuario a la caja de entrada de texto
                    if self.text == "Name" or self.text == "Password":
                        self.text = event.unicode
                    else:
                        self.text += event.unicode

                        
                # Actualiza el texto que se muestra en la caja de entrada de texto
                self.txt_surface = self.font.render(self.text, True, self.color)

    def draw(self, screen):
        # Dibuja la caja de entrada de texto en la pantalla
        pg.draw.rect(screen, self.color, self.rect, 2)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
    #pg.init()

# SCREEN_WIDTH = 640
# SCREEN_HEIGHT = 480
# BG_COLOR = (60, 60, 60)

# screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pg.display.set_caption("Inicio de sesión")

# username_box = InputBox(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 - 50, 200, 30, "Name")
# password_box = InputBox(SCREEN_WIDTH/2 - 100, SCREEN_HEIGHT/2 + 20, 200, 30, "Password")

# running = True

# # Dibujar la pantalla de inicio de sesión
# screen.fill(BG_COLOR)
# username_box.draw(screen)
# password_box.draw(screen)
# pg.display.flip()


# while running:
# # Manejar eventos del teclado y la pantalla
#     for event in pg.event.get():
#         # Dibujar la pantalla de inicio de sesión
#         screen.fill(BG_COLOR)
#         username_box.draw(screen)
#         password_box.draw(screen)
#         username_box.handle_event(event)
#         password_box.handle_event(event)
#         pg.display.flip()

#         if event.type == pg.QUIT:
#             running = False
            
#             pg.quit()

