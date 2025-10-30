# TTS Speed Control Guide

## Overview

You can control the speed of Text-to-Speech (TTS) pronunciation in the Korean
Pronunciation Trainer.

## Default Speed

The default TTS speed is set to **0.7** (70% of normal speed), which is slower
than natural speech to help with pronunciation learning.

## How to Change TTS Speed

### Method 1: Browser Console (Quick)

1. Open your browser's Developer Tools:
   - Chrome/Edge: Press `F12` or `Ctrl+Shift+I` (Windows/Linux) or
     `Cmd+Option+I` (Mac)
   - Firefox: Press `F12` or `Ctrl+Shift+K` (Windows/Linux) or `Cmd+Option+K`
     (Mac)
   - Safari: Enable Developer menu first, then press `Cmd+Option+C`

2. Go to the **Console** tab

3. Type the following command and press Enter:
   ```javascript
   setTTSSpeed(1.0);
   ```

### Method 2: Edit JavaScript File (Permanent)

To permanently change the default speed:

1. Open `static/javascript/callbacks.js`
2. Find the line:
   ```javascript
   let ttsSpeed = 0.7;
   ```
3. Change `0.7` to your desired speed
4. Refresh the browser

## Speed Values

| Speed     | Description | Use Case                        |
| --------- | ----------- | ------------------------------- |
| 0.1 - 0.4 | Very Slow   | Detailed pronunciation analysis |
| 0.5 - 0.6 | Slow        | Beginner learners               |
| 0.7       | Default     | Comfortable learning pace       |
| 0.8 - 0.9 | Moderate    | Intermediate learners           |
| 1.0       | Normal      | Natural Korean speech speed     |
| 1.1 - 1.5 | Fast        | Advanced learners               |
| 1.6 - 2.0 | Very Fast   | Native-level practice           |

## Examples

```javascript
// Very slow for detailed study
setTTSSpeed(0.5);

// Normal natural speed
setTTSSpeed(1.0);

// Fast for native-level practice
setTTSSpeed(1.5);

// Back to default
setTTSSpeed(0.7);
```

## Tips

1. Start with **0.5-0.7** if you're a beginner
2. Gradually increase to **0.8-1.0** as you improve
3. Use **1.5-2.0** only when practicing at native speed
4. The speed applies to:
   - Sample sentence playback
   - Individual word playback
   - All TTS in the application

## Troubleshooting

**Problem: Speed change doesn't work**

- Make sure you're typing the command in the browser console, not in the text
  field
- Refresh the page and try again
- Check if your browser supports Web Speech API

**Problem: Speed is too fast/slow even at 1.0**

- This depends on your browser's TTS engine
- Different browsers may have slightly different speeds
- Try adjusting in 0.1 increments to find your ideal speed

## Browser Compatibility

The TTS speed control works with browsers that support Web Speech API:

- Chrome/Chromium: Full support
- Edge: Full support
- Safari: Full support
- Firefox: Limited support (may vary by OS)

---

**Current TTS Speed**: Check browser console when page loads
