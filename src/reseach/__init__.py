from tkinter import HORIZONTAL, Frame, Scale, Tk

import Adafruit_PCA9685


# по умолчанию, если не введен адрес устройства, используется адрес 0x40
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)


class App:

    def __init__(self, master):
        frame = Frame(master)
        frame.pack()
        scale = Scale(frame, from_=0, to=360,
                      orient=HORIZONTAL, command=self.update)
        scale.grid(row=0)

    def update(self, angle):
        pulse_len = int(float(angle) * 500.0 / 180.0) + 110
        pwm.set_pwm(0, 0, pulse_len)
        pwm.set_pwm(1, 0, pulse_len)


root = Tk()
root.wm_title('Servo Control')
app = App(root)
root.geometry("200x50+0+0")
root.mainloop()
