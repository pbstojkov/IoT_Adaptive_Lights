from sense_hat import SenseHat

class Light:
    def __init__(self):
        self.X = [0, 0, 0]  # Red
        self.O = [255, 255, 255]  # White
        self.sketch = [
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X
        ]
        self.sense = SenseHat()

    def update_sketch(self):
        self.sketch = [
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X,
            self.X, self.X, self.X, self.X, self.X, self.X, self.X, self.X
        ]
    def change_color(self, r , g, b):
        self.X = [int(r), int(g), int(b)]
        self.update_sketch()
        self.sense.set_pixels(self.sketch)

    def low_light(self, intensity): #bool
        self.sense.low_light = intensity

my_light = Light()
my_light.change_color(0, 0, 0)



# from sense_hat import SenseHat
#
# X = [255, 0, 0]  # Red
# # X = [0, 0, 0]  # Red
# O = [255, 255, 255]  # White
# O = [155, 155, 155]  # White
#
# while True:
#     sense = SenseHat()
#     #bla bla
#     # sense.show_message("R2D2 was here")
#     question_mark = [
#     X, X, X, X, X, X, X, X,
#     X, X, X, X, X, X, X, X,
#     X, X, X, X, X, X, X, X,
#     X, X, X, X, X, X, X, X,
#     X, X, X, X, X, X, X, X,
#     X, X, X, X, X, X, X, X,
#     X, X, X, X, X, X, X, X,
#     X, X, X, X, X, X, X, O
#     ]
#     sense.low_light = True
#     sense.set_pixels(question_mark)
#     #sense.show_message("")
#     sense.set_pixels(question_mark)

