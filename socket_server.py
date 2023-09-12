import sys
import socket
import numpy
import re
import _thread

port = 8124
ThreadCount = 0

# Draw the top border of the canvas
def top_border(canvas):
    result = ""

    for i in range(len(canvas) + 2):
        if i == 0:
            result = "╔"
        elif i == len(canvas) + 1:
            result += "╗"
        else:
            result += "═"

    return result

# Draw the bottom border of the canvas
def bottom_border(canvas):
    result = ""

    for i in range(len(canvas) + 2):
        if i == 0:
            result += "╚"
        elif i == len(canvas) + 1:
            result += "╝"
        else:
            result += "═"

    return result

# Render the canvas
def render_canvas(canvas):
    result = f"{top_border(canvas)}\r\n"

    # render the insides of the canvas without the top and bottom borders
    for i in range(len(canvas)):
        result += "║"
        for j in range(len(canvas[i])):
            result += canvas[i][j]

        result += "║"
        result += "\r\n"

    result += bottom_border(canvas)
    result += "\r\n\r\n"
    return result

# Set the 2d (30 x 30) array reprensenting the canvas into an empty array.
# The array is just filled with empty spaces
def initialize_canvas():
    canvas = numpy.zeros((30, 30), "U1")
    canvas.fill(" ")

    return canvas

# Execute the `step <n>` command
# num_steps --> Number of steps to move the cursor 
# direction --> The direction to move the cursor
# brush_mode --> String representing what brush_mode to use: "draw", "hover", "erase"
# cursor --> Current index of the cursor in the canvas 2d arrat: It is just a 2d array of the format [y/row, x/col]
# canvas --> 30 x 30 2d array representing the canvas
def step(num_steps, direction, brush_mode, cursor, canvas):
    stroke = ""
    if brush_mode == "draw":
        stroke = "*"
    elif brush_mode == "eraser":
        stroke = " "

    border_end = len(canvas) - 1
    border_start = 0

    row = cursor[0]
    col = cursor[1]
    n = 0

    while (
        (row >= border_start and row <= border_end)
        and (col >= border_start and col <= border_end)
        and n < num_steps
    ):
        # only update the value in the current index
        # if stroke is either draw or erase 
        if stroke != "":
            canvas[row][col] = stroke

        r = row + direction[0]
        # new row is out of bounds then exit loop
        if r == -1 or r == len(canvas):
            break
  
        row = r

        c = col + direction[1]
        # new col is out of bounds then exit loop
        if c == -1 or c == len(canvas[0]):
            break

        col = c
        print(f"cursor: ({row}, {col})")
        n += 1

    return [row, col]

# Handles requests from a connected client
def client_handler(connection, interactive_mode):
    canvas = initialize_canvas()

    up = [-1, 0]
    up_right = [-1, 1]
    right = [0, 1]
    down_right = [1, 1]
    down = [1, 0]
    down_left = [1, -1]
    left = [0, -1]
    up_left = [-1, -1]
    directions = [up, up_right, right, down_right, down, down_left, left, up_left]
    direction_label = [
        "up",
        "up_right",
        "right",
        "down_right",
        "down",
        "down_left",
        "left",
        "up_left",
    ]
    current_direction = 0

    cursor = [15, 15]

    # initialize brush_mode to draw
    brush_mode = "draw"
    # let client know that we are connected
    connection.send("hello\r\n".encode())

    data = connection.recv(2048).decode()

    # get list of commands sent by client
    # Did this because unit tests send commands as an array
    list_of_commands = str(data).split("\r\n")

    while True:

        if not data:
            # if data is not received break
            break

        if len(list_of_commands) > 0:
            command = list_of_commands.pop(0).strip()
        else:
            data = connection.recv(2048).decode()
            list_of_commands = str(data).split("\r\n")
            command = list_of_commands.pop(0).strip()

        steps_cmd_pattern = re.compile("^steps\s\d+$")
        left_cmd_pattern = re.compile("^left(?: \d+)?$")
        right_cmd_pattern = re.compile("^right(?: \d+)?$")

        # steps <n>
        if steps_cmd_pattern.match(command) is not None:
            split = command.split(" ")
            number = int(split[1])
            cursor = step(
                number, directions[current_direction], brush_mode, cursor, canvas
            )

            if interactive_mode:
                connection.send("done...".encode())
        elif left_cmd_pattern.match(command) is not None: # left <n>
            split = command.split(" ")
            number = int(split[1]) if len(split) == 2 else 1
            current_direction = (current_direction - number) % len(directions)
            
            if interactive_mode:
                connection.send(f"direction is now: {direction_label[current_direction]}".encode())
        elif right_cmd_pattern.match(command) is not None: # right <n>
            split = command.split(" ")
            number = int(split[1]) if len(split) == 2 else 1
            current_direction = (current_direction + number) % len(directions)
            
            if interactive_mode:
                connection.send(f"direction is now: {direction_label[current_direction]}".encode())
        elif command == "hover":
            brush_mode = command
            
            if interactive_mode:
                connection.send("brush set to hover...".encode())
        elif command == "draw":
            brush_mode = command
            
            if interactive_mode:
                connection.send("brush set to draw...".encode())
        elif command == "eraser":
            brush_mode = command
            
            if interactive_mode:
                connection.send("brush set to eraser...".encode())
        elif command == "coord":
            response = f"({cursor[0]},{cursor[1]})\r\n"
            connection.send(response.encode())
        elif command == "render":
            response = f"{render_canvas(canvas)}"
            print(f"{response}")
            connection.send(response.encode())
        elif command == "clear":
            canvas = initialize_canvas()

            if interactive_mode:
                connection.send("canvas cleared...".encode())
        elif command == "quit":
            break
        # invalid command ignore and reprompt
        # Did this because unit test expect empty response
        # if user enters an invalid command.
        # Ideally I would like to return some sort of error message
        else:
            print(f"invalid command:{command}")
            if interactive_mode:
                connection.send("invalid command :(".encode())

    connection.close()  # close the connection

# Accepts new connections from a client
def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print(f"Connected to: " + address[0] + ":" + str(address[1]))
    interactive_mode = '-i' in sys.argv
    _thread.start_new_thread(client_handler, (Client, interactive_mode))

# Starts the server
def start_server(port):
    # get the hostname
    host = socket.gethostname()

    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        ServerSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    print(f"Server is listening on the port {port}...")
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)


if __name__ == "__main__":
    start_server(port)
