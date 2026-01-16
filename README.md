# Simple Chess Engine
<img width="873" height="665" alt="image" src="https://github.com/user-attachments/assets/a800cd13-90e2-44db-a3d7-199c1c99fa42" />

A minimalistic chess engine written in Python with a graphical user interface (GUI). This project demonstrates basic chess logic, board evaluation, and move generation, making it a great starting point for learning about chess programming and game development.

## Features

- Playable chess game with GUI
- Move validation and legal move generation
- Board evaluation using piece-square tables
- Simple AI engine for move selection
- Support for standard chess rules

## Project Structure

- `chess_gui.py`: Main file for the graphical user interface
- `engine.py`: Core chess engine logic (move generation, AI)
- `board_evaluator.py`: Board evaluation functions and piece-square tables
- `board_pieces_tables.py`: Piece-square tables and related data
- `requirements.txt`: Python dependencies

## Requirements

- Python 3.7+
- [python-chess](https://python-chess.readthedocs.io/) library

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/Simple-Chess-Engine.git
   cd Simple-Chess-Engine-main
   ```
2. (Optional) Create and activate a virtual environment:
   ```sh
   python -m venv env
   # Windows:
   .\env\Scripts\activate
   # Linux/macOS:
   source env/bin/activate
   ```
3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

Run the GUI application:

```sh
python chess_gui.py
```

## How It Works

- The GUI allows users to play chess against a simple AI.
- The engine generates legal moves and evaluates board positions using piece-square tables.
- The AI selects moves based on board evaluation scores.

## Contributing

Contributions are welcome! Feel free to open issues or submit pull requests to improve the engine, add features, or enhance the GUI.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [python-chess](https://github.com/niklasf/python-chess) for chess logic and utilities.
