# TCP Server

## About

A TCP server implementing a simple protocol very loosely inspired by [LOGO](<https://en.wikipedia.org/wiki/Logo_(programming_language)>). When a client connects, it will be able to send simple commands to the server to draw on a canvas. It will also call ask the server to render the current canvas.

## Specification

When a client connects, the server will allocate a canvas. The state of the canvas is defined by:

-   The canvas itself: a `30x30 buffer`.
-   The cursor, which is initially located at `(15,15)`.
-   The current direction, which is initially set to `top`.

The server opens a local TCP socket on `port 8124`. The server accepts commands separated by newlines `(\r\n)`. All server responses are also terminated by `\r\n`.

-   `steps <n>`: move the cursor n steps in the current direction.
-   `left <n>, right <n>`: change the direction (see “Directions” below).
-   `hover, draw, eraser`: set the brush mode (see “Drawing” below).
-   `coord`: print the current coordinates of the cursor with the format (x,y).
-   `render`: print the current canvas.
-   `clear`: erase the current canvas, while keeping the current cursor and direction.
-   `quit`: closes the current connection.

## Design

-   The server contains a 2d `(30 x 30)` array that represents the canvas.
-   The cursor starts at index `[15,15]`.
-   There is a `directions` array that represents all the 8 directions the cursor can move in. The values in the directions array are 2d array of the format `[y, x]`. The value in `[y]` represents which direction `y-axis` or `row direction` to move the cursor. Whereas the value in `[x]` represents which direction in the `x-axis` or `column direction` to move the cursor. As a result the 8 values stored in the `directions` array are:
    -   up = `[-1, 0]`
    -   up_right = `[-1, 1]`
    -   right = `[0, 1]`
    -   down_right = `[1, 1]`
    -   down = `[1, 0]`
    -   down_left = `[1, -1]`
    -   left = `[0, -1]`
    -   up_left = `[-1, -1]`
-   There is a `current_direction` variable that stores the current direction the cursor should move in. `current_direction` is mapped to an index in the `directions` array. So for example, if `current_direction = 0` and the directions arrray is `[[-1, 0], [-1, 1], [0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1]]`then it means the current direction of cursor is `[-1, 0]` which is equal to `top`.
-   The `current_direction` variable wraps around the `directions` array. So if for example `current_direction = 0` and a user types in `right 9`, the `current_direction` will be `9 % 8 = [1]` in the `directions` array.

## Running

-   To run the server, open a terminal and `cd` into this project's directory. Then simply run: `python3 socket_server.py -i`.
    -   Caveat: For unit tests, just run `python3 socket_server.py` --> Removes the verbose prompting sent to the user indicating that an action was completed.

##

-   To close server just enter `Ctrl + C` or `cmd + C` in the terminal
