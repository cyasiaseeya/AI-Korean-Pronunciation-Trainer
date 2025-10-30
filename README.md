# Korean AI Pronunciation Trainer

An AI-powered tool to evaluate and improve your Korean pronunciation. Get
objective, real-time feedback on your speaking skills using advanced speech
recognition and phonetic analysis.

## Features

- **Real-time pronunciation scoring** using Whisper ASR
- **Word-by-word and letter-by-letter feedback**
- **Browser-based Korean TTS** for reference audio
- **Sequential practice** with sentence counter
- **Web-based** - works on any platform with a modern browser
- **Dynamic sentence loading** - automatically adjusts to CSV file size

## Quick Start

### Local Installation

1. **Clone or download this repository**

2. **Install dependencies:**

```bash
pip install -r requirements.txt
```

3. **Install ffmpeg** (required for audio processing):
   - **Mac**: `brew install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)
   - **Linux**: `sudo apt-get install ffmpeg`

4. **Run the application:**

```bash
python3 webApp.py
```

5. **Open your browser** at `http://127.0.0.1:3000/`

**Note:** Debug mode is enabled by default, so the server will automatically
restart when you make changes to Python files.

### Requirements

- Python 3.11+ (tested with 3.11 and 3.12)
- Modern browser (Chrome/Edge recommended)
- Microphone access
- Korean TTS voice (usually built into modern browsers)

## How to Use

1. **Read the displayed Korean sentence** (sentences appear sequentially)
2. **Click the microphone** button to start recording
3. **Speak the sentence** aloud in Korean
4. **Click the microphone** again when done
5. **Get instant feedback** with:
   - Overall pronunciation accuracy score
   - Color-coded word accuracy (green=correct, orange=okay, red=incorrect)
   - Sentence progress tracker (e.g., "Sentence 3/28")
6. **Click "Next"** (→) to advance to the next sentence
7. **Refresh the page** to restart from sentence 1

## Technical Architecture

### Quick Overview

```
Your Speech → Whisper ASR → Korean Text → Epitran → IPA Phonemes
                                                           ↓
Expected Text → Epitran → IPA Phonemes                     ↓
                                    ↓                      ↓
                                    └──→ DTW Alignment ←───┘
                                              ↓
                                    Compare Phonemes (Edit Distance)
                                              ↓
                                    Calculate Accuracy Score
                                              ↓
                                    Color-Coded Visual Feedback
```

### Backend (Python)

- **Whisper ASR**: OpenAI's multilingual speech recognition
- **Epitran**: Korean to IPA phoneme conversion
- **Flask**: Web server
- **Dynamic Time Warping**: Word alignment algorithm

### Frontend (JavaScript)

- **Web Speech API**: Browser-based Korean TTS
- **MediaRecorder API**: Audio recording
- **Vanilla JavaScript**: No framework dependencies

### How It Works: Detailed Explanation

The pronunciation scoring system uses a multi-step pipeline that combines speech
recognition, phonetic analysis, and intelligent word alignment:

#### Step 1: Speech Recognition

When you record your pronunciation, the audio is sent to **Whisper ASR**
(Automatic Speech Recognition), OpenAI's multilingual speech recognition model.
Whisper transcribes your Korean speech into text, attempting to understand what
words you actually said.

**Example:**

- Expected: "안녕하세요"
- You said: "안녕세요" (missing 하)
- Whisper transcribes: "안녕세요"

#### Step 2: Phonetic Conversion (IPA)

Both the expected sentence and your transcribed speech are converted to **IPA
(International Phonetic Alphabet)** notation using the Epitran library. IPA
represents the actual sounds of the language, which is crucial for accurate
pronunciation comparison.

**Why IPA?** Korean spelling doesn't always match pronunciation due to
phonological rules. IPA captures how words actually sound.

**Example:**

- Text: "안녕하세요"
- IPA: "annjʌŋhasʰejo"

This conversion ensures we're comparing actual pronunciation, not just spelling.

#### Step 3: Word Alignment (DTW)

The system uses **Dynamic Time Warping (DTW)**, a sophisticated algorithm that
intelligently matches the words you spoke with the expected words. This handles
cases where you might have:

- Skipped a word
- Added an extra word
- Said words in a slightly different order
- Mispronounced individual words

DTW finds the best possible alignment between what you said and what was
expected, so each spoken word is matched to its corresponding expected word.

#### Step 4: Phoneme-Level Comparison

For each aligned word pair, the system calculates similarity using the
**Levenshtein Edit Distance** algorithm. This measures how many individual sound
changes (insertions, deletions, substitutions) would be needed to transform your
pronunciation into the correct pronunciation.

**Example:**

- Expected (IPA): "hasʰejo" (하세요)
- You said (IPA): "hasejo" (하세요, but without aspiration)
- Edit distance: 1 change needed (add aspiration to 's')
- Accuracy: 85% (very close!)

The fewer changes needed, the higher your pronunciation accuracy for that word.

#### Step 5: Overall Scoring

The system calculates:

1. **Word-level accuracy**: Each word gets a score based on phoneme similarity
2. **Overall accuracy**: Average across all words in the sentence
3. **Color coding**: Visual feedback helps you quickly identify problem areas
   - Green: Excellent pronunciation (80%+)
   - Orange: Good, minor improvements needed (60-79%)
   - Red: Needs work (below 60%)

#### Step 6: Visual Feedback

Results are displayed with:

- Color-coded words showing which parts were pronounced well
- Overall percentage score
- Cumulative score tracking for motivation

### Why This Approach Works

**Phoneme-based comparison** is more accurate than simple word matching because:

1. **Language-specific**: IPA captures Korean-specific sounds that don't exist
   in other languages
2. **Pronunciation rules**: Handles Korean phonological rules (e.g., 받침 final
   consonants, sound changes)
3. **Granular feedback**: Identifies exactly which sounds need improvement, not
   just wrong words
4. **Objective measurement**: Uses mathematical distance metrics, not subjective
   judgment
5. **Forgiving alignment**: DTW ensures you get credit for words you pronounce
   correctly, even if you skip or add words

**Limitations to be aware of:**

- Background noise can affect speech recognition accuracy
- Very strong accents might be transcribed differently than intended
- The system evaluates pronunciation, not grammar or naturalness
- Scores are comparative - they measure similarity to expected pronunciation,
  not absolute correctness

## Scoring System

### Understanding Your Score

Your pronunciation accuracy is calculated based on phoneme-level similarity
between your speech and the correct pronunciation. The score reflects how
closely your pronunciation matches native Korean pronunciation patterns.

#### Score Ranges

- **80-100% (Green)**: Excellent pronunciation
  - Your pronunciation is highly accurate
  - Only minor differences from native pronunciation
  - Native speakers would easily understand you
- **60-79% (Orange)**: Good pronunciation with room for improvement
  - Generally understandable pronunciation
  - Some phonemes or sound patterns need refinement
  - May have slight accent or unclear articulation
- **Below 60% (Red)**: Needs significant improvement
  - Major pronunciation issues that could affect understanding
  - Missing or incorrect phonemes
  - Recommend repeating the sentence and focusing on correct sounds

#### What Affects Your Score?

1. **Phoneme accuracy**: Each Korean sound must be pronounced correctly
2. **Aspiration**: Korean distinguishes between aspirated (ㅋ, ㅌ, ㅍ, ㅊ) and
   unaspirated consonants (ㄱ, ㄷ, ㅂ, ㅈ)
3. **Vowel quality**: Korean has vowel distinctions not found in many languages
4. **Word completeness**: Skipping syllables or words significantly reduces
   score
5. **Speech clarity**: Background noise or mumbling can affect recognition

### Progress Tracking

- Sentences are presented **sequentially** from the database
- The sentence counter shows your current position (e.g., "Sentence 5/28")
- Refreshing the page resets to the first sentence
- Your cumulative score is tracked throughout the session

## Project Structure

```
ai-pronunciation-trainer/
├── webApp.py                 # Flask server (debug mode enabled)
├── pronunciationTrainer.py   # Core evaluation logic
├── whisper_wrapper.py        # Whisper ASR interface
├── RuleBasedModels.py        # Korean phoneme converter
├── models.py                 # Model factory
├── lambdaGetSample.py        # Sample sentence retrieval
├── lambdaSpeechToScore.py    # Pronunciation scoring
├── databases/
│   └── data_ko.csv          # Korean sentences database (28 sentences)
├── static/
│   ├── css/
│   └── javascript/
│       └── callbacks.js     # Frontend logic
└── templates/
    └── main.html            # Web interface
```

**Note:** All code comments are written in Korean (한국어).

## Customization

### Adding Your Own Sentences

Edit `databases/data_ko.csv` to add or modify sentences:

```csv
sentence
안녕하세요
좋은 아침입니다
당신의 한국어 문장을 여기에 추가하세요
```

**Note:** The sentence counter automatically updates based on the number of
sentences in your CSV file. Add or remove sentences freely - no code changes
needed!

### Adjusting Scoring Thresholds

In `pronunciationTrainer.py`:

```python
categories_thresholds = np.array([80, 60, 59])  # Good, Okay, Bad
```

## Browser Compatibility

| Browser | Windows | macOS | Linux |
| ------- | ------- | ----- | ----- |
| Chrome  | Yes     | Yes   | Yes   |
| Edge    | Yes     | Yes   | Yes   |
| Firefox | Yes     | Yes   | Yes   |
| Safari  | N/A     | Yes   | N/A   |

_Note: Chrome/Edge recommended for best Korean TTS quality_

## Troubleshooting

### No sound from TTS

- Ensure your browser supports the Web Speech API
- Check system volume and browser permissions
- Korean TTS voice may need to be installed (usually automatic in modern
  browsers)

### Changes not appearing

- **Python files** (.py): Server auto-reloads thanks to debug mode - just save
  and wait a moment
- **HTML/CSS/JS files**: Just **hard refresh** your browser: `Cmd+Shift+R` (Mac)
  or `Ctrl+Shift+R` (Windows/Linux)
- No need to manually restart the server!

### Audio processing is slow

- First recording after server start will be slower (model loading)
- Ensure adequate RAM (2GB+ recommended)
- Close other memory-intensive applications

### Microphone not working

- Check browser permissions (allow microphone access)
- Ensure no other application is using the microphone
- Try a different browser if issues persist

## Deployment

### Development Server

For testing or single-user demos (e.g., Capstone projects), the built-in Flask
server is sufficient:

```bash
python3 webApp.py
```

Debug mode is enabled by default for faster development (auto-reload on file
changes).

### Production Deployment

**Important:** For production, consider disabling debug mode in `webApp.py` by
changing `debug=True` to `debug=False` for security and performance.

### System Requirements

- **RAM**: Minimum 2GB recommended for Whisper-base model
  - First audio transcription will be slower (model loading)
  - Subsequent transcriptions: ~5-10 seconds per recording
- **Storage**: ~500MB for dependencies and models
- **Network**: Not required after initial model download

## 📝 License

GNU Affero General Public License v3.0 (AGPL-3.0)

See [LICENSE](LICENSE) file for details.

## Acknowledgments

- Original project by
  [Thiago Lobato](https://github.com/Thiagohgl/ai-pronunciation-trainer)
