# Float Cards

An Anki addon that creates a floating window to display the current card with custom intervals, allowing you to review cards while doing other tasks.

<img src="https://raw.githubusercontent.com/BrenoAqua/Float-Cards/refs/heads/main/preview-images/Default.png" width="35%">
<img src="https://raw.githubusercontent.com/BrenoAqua/Float-Cards/refs/heads/main/preview-images/Background%20Active.png" width="35%">

## Features

- Floating window
- Option to keep the window always on top
- Syncs with the main Anki window and closes along with the deck
- Support for light/dark themes
- Keyboard hotkey support, allowing multiple hotkeys for the same function
- Scheduling with configurable intervals and auto-close functionality
- Custom background image support with opacity control
- Configurable button visibility and styling
- Minimal interface
- Content scaling (50-200%)
- Hardware acceleration and image optimization
- Quick loading of next cards
- Remembers position, content scaling and window memory between sessions

## Installation

1. Download the addon from [AnkiWeb](https://ankiweb.net/shared/info/17442591)
2. Restart Anki
3. Access the addon through Float Cards > Toggle Float Cards/Config

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

<div style="display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; max-width: 70%;">
    <img src="https://raw.githubusercontent.com/BrenoAqua/Float-Cards/refs/heads/main/preview-images/config/General.png" width="45%">
    <img src="https://raw.githubusercontent.com/BrenoAqua/Float-Cards/refs/heads/main/preview-images/config/Background.png" width="45%">
    <img src="https://raw.githubusercontent.com/BrenoAqua/Float-Cards/refs/heads/main/preview-images/config/Buttons.png" width="45%">
    <img src="https://raw.githubusercontent.com/BrenoAqua/Float-Cards/refs/heads/main/preview-images/config/Hotkeys.png" width="45%">
</div>


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

![anki_oKofQZkD18](https://github.com/user-attachments/assets/392bd57e-4271-4ac0-96ba-808057ad6976)

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
1. Enable scheduling in the "Select Deck" window
2. Select your target deck
3. Set the interval
4. Optionally enable auto-close
5. Set the number of answers before auto-closing

## Requirements

- Anki 23.10+
