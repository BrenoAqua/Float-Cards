# Float Cards

An Anki addon that creates a floating window to display the current card with custom intervals, allowing you to review cards while doing other tasks.

<img src="https://github.com/user-attachments/assets/8e210aaf-f998-4a5f-a128-04f782f9d1aa" width="35%">
<img src="https://github.com/user-attachments/assets/7d5e34c7-2a54-4ba6-aaac-011d49244110" width="35%">

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

<img src="https://github.com/user-attachments/assets/5f0b4d9c-7273-4f11-a83a-f71db337d9e2" width="32.5%">
<img src="https://github.com/user-attachments/assets/d8e97bd7-0918-45fb-8a35-1bb7c2aaf780" width="32.5%">
<img src="https://github.com/user-attachments/assets/ef883bca-3f17-4065-a51f-b44f63bc4283" width="32.5%">
<img src="https://github.com/user-attachments/assets/1208b331-0339-4c78-a15b-313f365967f1" width="32.5%">
<img src="https://github.com/user-attachments/assets/9e223ca9-909e-4a6d-9f75-3b3506283a2e" width="32.5%">

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
1. Enable scheduling in the config
2. Select your target deck
3. Set the interval
4. Optionally enable auto-close
5. Set the number of answers before auto-closing

## Requirements

- Anki 23.10+
