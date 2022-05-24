import pygame
pygame.init()
class Button:
    def __init__(self,width,height):
        self.width =width
        self.height = height
        self.inactive_color = (23,204,58)
        self.active_color = (13,162,58)
        self.button_sound = pygame.mixer.Sound('audio/button.wav')
        self.font = pygame.font.Font('font/Pixeled.ttf', 20)

    def draw(self,x,y,message,display,action = None):
        pygame.init()
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()

        if x<mouse[0]<x+self.width:
            if y < mouse[1] < y + self.height:
                pygame.draw.rect(display,self.active_color,(x,y,self.width,self.height))

                if click[0] == 1:
                    pygame.mixer.Sound.play(self.button_sound)
                    pygame.time.delay(300)
                    if action is not None:
                        action()
        else:
            pygame.draw.rect(display,self.inactive_color,(x,y,self.width,self.height))
        text = self.font.render(message,True,(0,0,0))
        display.blit(text,(x+10,y+10))
