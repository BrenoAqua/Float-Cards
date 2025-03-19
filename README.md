# Float Cards

An Anki addon that creates a floating window to display the current card with custom intervals, allowing you to review cards while doing other tasks.

<img src="https://github.com/user-attachments/assets/8e210aaf-f998-4a5f-a128-04f782f9d1aa" width="35%">
<img src="https://github.com/user-attachments/assets/7d5e34c7-2a54-4ba6-aaac-011d49244110" width="35%">

## Features

- Floating window that stays on top (optional)
- Syncs with main Anki window, closes the deck together with the pop-up
- Support for light/dark themes
- Keyboard shortcut support with support for multiple hotkeys for the same function 
- Scheduling with intervals and auto-close functionality
- Custom background image support with opacity control
- Configurable button visibility and styling
- Minimal interface
- Content scaling (50-200%)
- Hardware acceleration and image optimization
- Quick loading of next cards
- Position, content scaling and window memory between sessions

## Installation

1. Download the addon from [AnkiWeb](https://ankiweb.net/shared/info/17442591)
2. Restart Anki
3. Access the addon through Float Cards > Toggle Float Cards/COnfigure

## Configuration

Access the addon through Float Cards > Toggle Float Cards/Config

- Window size and position
- Stay on top behavior
- Theme customization
- Content scaling
- Background image and opacity
- Button visibility and styling
- Keyboard hotkeys
- Performance settings

<img src="https://github.com/user-attachments/assets/689d5234-74be-495b-b08c-2b5c58818b23" width="32.5%">
<img src="https://github.com/user-attachments/assets/2999ae8b-3452-4968-a528-4052e6ec64cf" width="32.5%">
<img src="https://github.com/user-attachments/assets/73015871-d242-49aa-b358-8423480eddcc" width="32.5%">

### Default Keyboard Hotkeys

| Action | Hotkey |
|--------|----------|
| Show/Hide Window | Ctrl+Shift+M |
| Toggle Stay on Top | Ctrl+T |
| Toggle Scheduling | Ctrl+Alt+S |
| Toggle Auto-close | Ctrl+Alt+A |
| Show Answer | Space |
| Again | 1 |
| Hard | 2 |
| Good | 3 |
| Easy | 4 |
| Play Audio | R |
| Play Second Audio | Ctrl+R |
| Toggle Scale Dialog | Ctrl+Alt+Z |

## Usage

1. Press Ctrl+Shift+M (default) or use Float Cards > Toggle Float Cards to show/hide the window

![anki_QbXsCkPi3D](https://github.com/user-attachments/assets/87d2c6d9-cc9d-4737-96b8-0e3eeb60ab00)

2. Review cards as normal
3. Audio playback works just like in the main window
4. Answer buttons work the same as in the main window
5. Use Ctrl+Alt+S to toggle scheduling
6. Use Ctrl+Alt+A to toggle auto-close
7. Use Ctrl+T to toggle stay-on-top
8. Use Ctrl+Alt+Z to adjust content scaling

### Background Image

You can set a custom background image for the popup window:
1. Enable background in the config
2. Set the path to your image
3. Adjust the opacity (0-100)
4. The image will be displayed behind the card content

### Scheduling

The addon supports automatic card scheduling:
1. Enable scheduling in the config
2. Select your target deck
3. Set the interval
4. Optionally enable auto-close
5. Set the number of answers before auto-closing

## Requirements

- Anki 23.10+
