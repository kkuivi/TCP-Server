import socket
import numpy
import re
import _thread

port = 8124
ThreadCount = 0


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


def render_canvas(canvas):
    result = f"{top_border(canvas)}\r\n"

    for i in range(len(canvas)):
        result += "║"
        for j in range(len(canvas[i])):
            result += canvas[i][j]

        result += "║"
        result += "\r\n"

    result += bottom_border(canvas)
    result += "\r\n\r\n"
    return result


def initialize_canvas():
    canvas = numpy.zeros((30, 30), "U1")
    canvas.fill(" ")

    return canvas


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
        if stroke != "":
            canvas[row][col] = stroke

        r = row + direction[0]
        if r == -1 or r == len(canvas):
            break
        row = r

        c = col + direction[1]
        if c == -1 or c == len(canvas[0]):
            break

        col = c
        n += 1

    print("steps done...")
    print(f"row: {row}  | col: {col}")
    return [row, col]


def client_handler(connection):
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

    brush_mode = "draw"
    connection.send("hello\r\n".encode())

    data = connection.recv(2048).decode()

    list_of_commands = str(data).split("\r\n")
    print(f"{list_of_commands}")

    response = ""
    while True:
        if not data:
            # if data is not received break
            break

        print(f"{list_of_commands}")

        if len(list_of_commands) > 0:
            command = list_of_commands.pop(0).strip()
            print(f"curr command: {command}")
        else:
            data = connection.recv(2048).decode()
            list_of_commands = str(data).split("\r\n")
            command = list_of_commands.pop(0).strip()

        steps_cmd_pattern = re.compile("^steps\s\d+$")
        left_cmd_pattern = re.compile("^left(?: \d+)?$")
        right_cmd_pattern = re.compile("^right(?: \d+)?$")

        if steps_cmd_pattern.match(command) is not None:
            split = command.split(" ")
            number = int(split[1])
            cursor = step(
                number, directions[current_direction], brush_mode, cursor, canvas
            )
        elif left_cmd_pattern.match(command) is not None:
            split = command.split(" ")
            number = int(split[1]) if len(split) == 2 else 1
            current_direction = (current_direction - number) % len(directions)
        elif right_cmd_pattern.match(command) is not None:
            split = command.split(" ")
            number = int(split[1]) if len(split) == 2 else 1
            current_direction = (current_direction + number) % len(directions)
        elif command == "hover":
            brush_mode = command
            response = "brush_mode is now: hover...\r\n"
        elif command == "draw":
            brush_mode = command
            response = "brush_mode is now: draw...\r\n"
        elif command == "eraser":
            brush_mode = command
            response = "brush_mode is now: eraser...\r\n"
        elif command == "coord":
            response = f"({cursor[0]},{cursor[1]})\r\n"
            print(f"response is: {response}")
            connection.send(response.encode())  # send data to the client
        elif command == "render":
            response = f"{render_canvas(canvas)}"
            print(f"{response}")
            connection.send(response.encode())  # send data to the client
        elif command == "clear":
            canvas = initialize_canvas()
            response = f"cleared canvas!\r\n"
        elif command == "quit":
            response = "quit!\r\n"
            break
        else:
            print(f"invalid command:{command}")

    connection.close()  # close the connection


def accept_connections(ServerSocket):
    Client, address = ServerSocket.accept()
    print(f"Connected to: " + address[0] + ":" + str(address[1]))
    _thread.start_new_thread(client_handler, (Client,))


def start_server(port):
    # get the hostname
    host = socket.gethostname()

    ServerSocket = socket.socket()
    try:
        ServerSocket.bind((host, port))
    except socket.error as e:
        print(str(e))
    print(f"Server is listeningn on the port {port}...")
    ServerSocket.listen()

    while True:
        accept_connections(ServerSocket)


if __name__ == "__main__":
    start_server(port)
