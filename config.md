# Float Cards — Config
 *Changes to the config file require restarting Anki to take effect*

## Window Settings

- `window_width`: Width of the floating window in pixels (default: 485)
- `window_height`: Height of the floating window in pixels (default: 721)
- `position_x`: Initial X position of the window (default: 829)
- `position_y`: Initial Y position of the window (default: 78)
- `stay_on_top`: Whether the window should stay on top of other windows (default: true)
- `shortcut`: Global shortcut to show/hide the window (default: "Ctrl+Shift+M")

## Button Settings

### Button Visibility
- `buttons.show_again`: Show the Again button (default: true)
- `buttons.show_hard`: Show the Hard button (default: false)
- `buttons.show_good`: Show the Good button (default: true)
- `buttons.show_easy`: Show the Easy button (default: false)

### Button Styling
- `buttons.styles.height`: Height of buttons in pixels (default: 30)
- `buttons.styles.min_width`: Minimum width of buttons in pixels (default: 50)
- `buttons.styles.border_radius`: Border radius of buttons (default: 3)
- `buttons.styles.font_weight`: Font weight of button text (default: "bold")

### Button Colors
Each button (again, hard, good, easy, show_answer) has the following color properties:
- `background`: Default background color
- `background hover`: Background color when hovering
- `text`: Default text color
- `text hover`: Text color when hovering
- `border`: Border color

## Theme Settings

### Light Theme
- `theme.light.background`: Background color
- `theme.light.text`: Text color
- `theme.light.button_bg`: Button background color
- `theme.light.button_text`: Button text color
- `theme.light.button_border`: Button border color
- `theme.light.font_family`: Font family
- `theme.light.font_size`: Font size
- `theme.light.line_height`: Line height
- `theme.light.padding`: Padding in pixels

### Dark Theme
Same properties as light theme but for dark mode.

## Hotkeys

- `hotkeys.show_answer`: Show answer shortcut (default: "Space")
- `hotkeys.again`: Again button shortcut (default: "h")
- `hotkeys.hard`: Hard button shortcut (default: "")
- `hotkeys.good`: Good button shortcut (default: "j")
- `hotkeys.easy`: Easy button shortcut (default: "")
- `hotkeys.toggle_stay_on_top`: Toggle stay on top shortcut (default: "Ctrl+T")
- `hotkeys.replay_sound`: Replay sound shortcut (default: "R")
- `hotkeys.replay_second_sound`: Replay second sound shortcut (default: "Ctrl+R")
- `hotkeys.toggle_scheduling`: Toggle scheduling shortcut (default: "Ctrl+Alt+S")
- `hotkeys.toggle_auto_close`: Toggle auto close shortcut (default: "Ctrl+Alt+A")

## Scheduling Settings

- `scheduling.enabled`: Enable automatic scheduling (default: false)
- `scheduling.frequency`: How often to show cards (default: 1)
- `scheduling.deck`: Deck to schedule cards from (default: "Senren")
- `scheduling.auto_close_on_answer`: Automatically close window after answering (default: false)

## Background Settings

- `background.enabled`: Enable custom background (default: false)
- `background.image_path`: Path to background image
- `background.opacity`: Background opacity (0-100, default: 20)

## 
>Created by [@BrenoAqua](https://github.com/BrenoAqua)