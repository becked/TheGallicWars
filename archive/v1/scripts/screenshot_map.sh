#!/bin/bash
# screenshot_map.sh - Take a grid of screenshots across the game map
#
# Usage: ./scripts/screenshot_map.sh
#
# Tune these constants to get good coverage:

# Seconds to hold Shift+key when panning between screenshots
PAN_HOLD=0.2

# Seconds to hold Shift+key when going to the SW corner
CORNER_HOLD=5.0

# Seconds to wait before each screenshot (let rendering settle)
SCREENSHOT_DELAY=0.2

# Grid size (columns x rows)
COLS=5
ROWS=4

# Output directory
OUT_DIR="/tmp/map_screenshots"
rm -rf "$OUT_DIR"
mkdir -p "$OUT_DIR"

# Key codes: W=13, A=0, S=1, D=2
KC_W=13
KC_A=0
KC_S=1
KC_D=2

pan() {
    local keycode="$1"
    local hold_seconds="$2"
    osascript -e "
tell application \"OldWorld\" to activate
tell application \"System Events\"
    tell process \"OldWorld\"
        key down shift
        key down $keycode
        delay $hold_seconds
        key up $keycode
        key up shift
    end tell
end tell"
}

screenshot() {
    local name="$1"
    sleep "$SCREENSHOT_DELAY"
    screencapture -x "${OUT_DIR}/${name}.png"
    echo "  -> ${name}.png"
}

echo "=== Map Screenshot Grid (${COLS}x${ROWS}) ==="
echo "Settings: PAN_HOLD=${PAN_HOLD}s, CORNER_HOLD=${CORNER_HOLD}s, INSET_HOLD=${INSET_HOLD}s"
echo ""

# Step 1: Go to SW corner
#echo "Panning to SW corner..."
#pan $KC_S $CORNER_HOLD
#pan $KC_A $CORNER_HOLD

# Step 2: Take screenshots in a snake pattern
for (( row=0; row<ROWS; row++ )); do
    echo "Row $((row+1)) of $ROWS:"

    for (( col=0; col<COLS; col++ )); do
        name="r${row}_c${col}"
        screenshot "$name"

        # Pan east (unless last column)
        if (( col < COLS - 1 )); then
            pan $KC_D $PAN_HOLD
        fi
    done

    # Pan north for next row (unless last row)
    if (( row < ROWS - 1 )); then
        echo "  Panning north..."
        pan $KC_W $PAN_HOLD

        # Go back west to column 0
        # Hold west for (COLS-1) * PAN_HOLD seconds
        local west_hold
        west_hold=$(echo "$PAN_HOLD * ($COLS - 1)" | bc)
        pan $KC_A "$west_hold"
    fi
done

echo ""
echo "=== Done! Screenshots in $OUT_DIR ==="
ls -1 "$OUT_DIR"

# Return to Alacritty
osascript -e 'tell application "System Events" to tell process "alacritty" to set frontmost to true'
