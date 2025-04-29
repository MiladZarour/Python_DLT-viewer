# Python DLT Viewer

A pure Python application for viewing and analyzing DLT (Diagnostic Log and Trace) files used in automotive software diagnostics.

## Features

- Load and parse DLT (Diagnostic Log and Trace) files
- Filter messages by ECU ID, Application ID, Context ID, and log level
- Search functionality across message content
- Detailed message view with decoded information
- Hex view for raw message data
- Message bookmarking
- Customizable UI with light and dark themes

## Requirements

- Python 3.7 or higher
- Tkinter (usually included with Python)

## Installation

1. Clone this repository:
```
git clone https://github.com/yourusername/python-dlt-viewer.git
cd python-dlt-viewer
```

2. Run the application:
```
python main.py
```

## Usage

1. Start the application using `python main.py`
2. Open a DLT file using File > Open or Ctrl+O
3. Use the filter panel on the left to filter messages
4. Select a message to view its details
5. Use search functionality to find specific content

## Screenshots

(Screenshots would be added here in a real README)

## File Format Support

The application supports standard DLT file format according to the Automotive GENIVI Alliance specification.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.