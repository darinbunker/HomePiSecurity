import RPi.GPIO as io
io.setmode(io.BCM)

# io.setup(pir_pin, io.IN)         # activate input
io.setup(2, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(3, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(4, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(5, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(6, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(7, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(8, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(9, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(10, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(11, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(12, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(13, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(14, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(15, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(16, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(17, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(18, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(19, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(20, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(21, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(22, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(23, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(24, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(25, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(26, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp
io.setup(27, io.IN, pull_up_down=io.PUD_UP)  # activate input with PullUp

# Print out the status of the pin
print("Pin 02 Status: " + `io.input(2)`)
print("Pin 03 Status: " + `io.input(3)`)
print("Pin 04 Status: " + `io.input(4)`)
print("Pin 05 Status: " + `io.input(5)`)
print("Pin 06 Status: " + `io.input(6)`)
print("Pin 07 Status: " + `io.input(7)`)
print("Pin 08 Status: " + `io.input(8)`)
print("Pin 09 Status: " + `io.input(9)`)
print("Pin 10 Status: " + `io.input(10)`)
print("Pin 11 Status: " + `io.input(11)`)
print("Pin 12 Status: " + `io.input(12)`)
print("Pin 13 Status: " + `io.input(13)`)
print("Pin 14 Status: " + `io.input(14)`)
print("Pin 15 Status: " + `io.input(15)`)
print("Pin 16 Status: " + `io.input(16)`)
print("Pin 17 Status: " + `io.input(17)`)
print("Pin 18 Status: " + `io.input(18)`)
print("Pin 19 Status: " + `io.input(19)`)
print("Pin 20 Status: " + `io.input(20)`)
print("Pin 21 Status: " + `io.input(21)`)
print("Pin 22 Status: " + `io.input(22)`)
print("Pin 23 Status: " + `io.input(23)`)
print("Pin 24 Status: " + `io.input(24)`)
print("Pin 25 Status: " + `io.input(25)`)
print("Pin 26 Status: " + `io.input(26)`)
print("Pin 27 Status: " + `io.input(27)`)

io.cleanup()
