# AI-MEDICAL-SCRIBE-CLONE

Python MVP that follows your diagram workflow:

1. Record information by voice (doctor controlled)
2. Transcribe speech to text
3. Decipher into SOAP notes
4. Understand chief complaint
5. Show on-screen decision support in 3 areas:
	- Real-world evidence
	- Medical issues
	- Guidelines
6. Output report with references
7. Optionally email the report

It includes:

- CLI workflow (`main.py`)
- Website UI workflow (`streamlit_app.py`)

## Project Structure

- `main.py`: CLI entry point
- `src/medical_scribe/recorder.py`: voice recording
- `src/medical_scribe/transcriber.py`: speech-to-text
- `src/medical_scribe/analyzer.py`: SOAP + chief complaint extraction
- `src/medical_scribe/support.py`: evidence/issues/guideline engine with references
- `src/medical_scribe/display.py`: screen output formatter
- `src/medical_scribe/emailer.py`: SMTP email sender
- `src/medical_scribe/report.py`: report builder and file export
- `data/knowledge_base.json`: lightweight medical reference data
- `tests/test_pipeline.py`: unit tests
- `streamlit_app.py`: browser-based interface

## Quick Start

### 1. Create environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run with typed text (fastest demo)

```bash
python main.py --text "Patient reports headache and fever for 2 days, no chest pain, blood pressure 145/95, likely viral syndrome" --patient-id P-001
```

## Run Website UI

```bash
streamlit run streamlit_app.py
```

Then open the local Streamlit URL shown in terminal.

UI supports:

- Typed text input
- Upload `.wav`, `.aiff`, `.flac`, or `.txt`
- Browser microphone recording (if supported by installed Streamlit version)
- On-screen SOAP + decision support areas + references
- Download report as markdown
- Optional email send via SMTP environment variables

### 3. Run with an audio file

```bash
python main.py --audio-file sample.wav --patient-id P-002
```

### 4. Record from microphone for N seconds

```bash
python main.py --record-seconds 10 --patient-id P-003
```

### 5. Send output by email

Set SMTP environment variables:

```bash
export SMTP_HOST=smtp.gmail.com
export SMTP_PORT=587
export SMTP_USERNAME=your_email@gmail.com
export SMTP_PASSWORD=your_app_password
export SMTP_FROM=your_email@gmail.com
```

Then run:

```bash
python main.py --text "Patient has cough, wheeze, and shortness of breath" --send-email doctor@example.com
```

Reports are saved to `outputs/`.

## Notes

- This is an educational MVP, not a medical device.
- Clinical decisions must be validated by licensed clinicians.
- Transcription quality depends on microphone/audio quality.