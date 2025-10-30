# Noise Detection Enhancement Guide

Guide to the enhanced noise detection features for the Korean Pronunciation
Trainer with FasterWhisper.

## New Features

### 1. Automatic Noise Reduction

- Automatically detects and attenuates background noise
- Removes noise while minimizing voice distortion
- Energy-based noise gating

### 2. Enhanced VAD (Voice Activity Detection)

- 4 sensitivity levels: low, moderate, high, very_high
- Adjustable parameters based on environment
- More accurate voice segment detection

### 3. Audio Quality Monitoring

- Real-time SNR (Signal-to-Noise Ratio) estimation
- Silence ratio detection
- Quality warning messages

## Configuration

### Method 1: Edit config.py file (Recommended)

Open the `config.py` file and adjust the following settings:

```python
# Enable/disable noise reduction
ENABLE_NOISE_REDUCTION = True  # True or False

# Adjust VAD sensitivity
VAD_AGGRESSIVENESS = "moderate"  # "low", "moderate", "high", "very_high"

# Whisper model size
WHISPER_MODEL_SIZE = "small"  # "tiny", "base", "small", "medium", "large-v2"
```

### Method 2: Configure Directly in Code

When using `pronunciationTrainer.py`:

```python
trainer = getTrainer(
    language='ko',
    enable_noise_reduction=True,
    vad_aggressiveness='high',  # For noisy environments
    model_size='small'
)
```

## VAD Sensitivity Selection Guide

### Low Sensitivity

**When to use:**

- Quiet recording studio
- Using headset microphone
- Almost no background noise
- Need to capture soft voices

**Characteristics:**

- Recognizes more sounds as speech
- Captures soft pronunciations well
- May recognize noise as speech

---

### Moderate Sensitivity (Default)

**When to use:**

- General home environment
- Quiet office
- Minor background noise (keyboard, mouse, etc.)

**Characteristics:**

- Balanced setting
- Suitable for most environments
- Appropriate distinction between voice and noise

---

### High Sensitivity

**When to use:**

- Cafes, restaurants
- Office (multiple people)
- Air conditioner, fan noise
- Street noise audible environment

**Characteristics:**

- Actively filters background noise
- Recognizes only clear speech
- Better focus on pronunciation practice

---

### Very High Sensitivity

**When to use:**

- Very noisy environment
- Cafe/bar during busy hours
- Environment with multiple people talking simultaneously
- Music or TV playing

**Characteristics:**

- Most selective voice detection
- Recognizes only clear and loud voices
- Minimizes noise false positives
- May not detect very soft voices

## Practical Usage Examples

### Example 1: Home Use (Default)

```python
# config.py
ENABLE_NOISE_REDUCTION = True
VAD_AGGRESSIVENESS = "moderate"
WHISPER_MODEL_SIZE = "small"
```

Works well in most cases.

---

### Example 2: Cafe Use

```python
# config.py
ENABLE_NOISE_REDUCTION = True
VAD_AGGRESSIVENESS = "high"  # or "very_high"
WHISPER_MODEL_SIZE = "small"
```

Effectively filters background noise.

---

### Example 3: Quiet Environment + High Quality

```python
# config.py
ENABLE_NOISE_REDUCTION = False  # Not necessary
VAD_AGGRESSIVENESS = "low"
WHISPER_MODEL_SIZE = "small"  # or "medium"
```

Provides best accuracy and sensitivity.

---

### Example 4: Laptop Microphone

```python
# config.py
ENABLE_NOISE_REDUCTION = True
VAD_AGGRESSIVENESS = "moderate"  # or "high"
WHISPER_MODEL_SIZE = "small"
```

Filters laptop fan noise and keyboard sounds.

## Troubleshooting

### Problem: "Voice not being recognized well"

**Solution:**

1. Lower VAD sensitivity: "low" or "moderate"
2. Move microphone closer to mouth
3. Speak louder and more clearly

### Problem: "Background noise being recognized as speech"

**Solution:**

1. Increase VAD sensitivity: "high" or "very_high"
2. Verify `ENABLE_NOISE_REDUCTION = True`
3. Move to quieter environment

### Problem: "Quality warnings keep appearing"

**Solution:**

1. Check microphone input level (not too low or high)
2. Adjust microphone position
3. Reduce background noise
4. Consider using a better microphone

### Problem: "Processing speed too slow"

**Solution:**

1. Use smaller model: `WHISPER_MODEL_SIZE = "tiny"` or `"base"`
2. Verify `USE_FASTER_WHISPER = True`
3. Check CUDA support if GPU available

## Performance Comparison

| Setting         | Speed | Accuracy | Noise Filtering | Memory |
| --------------- | ----- | -------- | --------------- | ------ |
| tiny + low      | 5/5   | 2/5      | 2/5             | 5/5    |
| base + moderate | 4/5   | 4/5      | 4/5             | 4/5    |
| small + high    | 3/5   | 5/5      | 5/5             | 3/5    |
| medium + high   | 2/5   | 5/5      | 5/5             | 2/5    |

## Additional Tips

1. **Microphone Test**: Test with various settings first
2. **Consistency**: Use same settings in same environment
3. **Gradual Adjustment**: Change only one setting at a time
4. **Check Logs**: Monitor quality warning messages in console
5. **Regular Updates**: Keep `faster-whisper` package up to date

## Check Configuration

To verify current settings:

```bash
cd /Users/cyasiaseeya/Desktop/AI-Korean-Pronunciation-Trainer
python3 config.py
```
