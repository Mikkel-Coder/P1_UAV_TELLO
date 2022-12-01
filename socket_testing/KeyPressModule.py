import pygame


def init():
    pygame.init()
    win = pygame.display.set_mode((400, 400))


def getKey(keyName):
    ans = False
    for eve in pygame.event.get():
        # print(eve)
        pass
    keyInput = pygame.key.get_pressed()
    # print(keyInput)
    myKey = getattr(pygame, 'K_{}'.format(keyName))
    if keyInput[myKey]:
        ans = True
    # pygame.display.update()
    return ans


def main():
    if getKey('LEFT'):
        print('Left key pressed')
    if getKey('RIGHT'):
        print('right key pressed')    


if __name__ == '__main__':
    init()
    while True:
        main()
