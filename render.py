from PIL import Image

board = Image.open("assets/board.png")

board.save("game.png")

print("Поле сохранено")