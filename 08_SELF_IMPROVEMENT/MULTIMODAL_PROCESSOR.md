# MULTI-MODAL PROCESSOR — Images, Audio, Video, Documents

## Filosofie

SENTINEL trebuie să proceseze **toate tipurile de input** pe care Popy le poate furniza. Nu doar text. Pattern-uri autentice vin din mai multe forme.

## Tipuri de Input

### 1. Imagini
- Format: PNG, JPG, JPEG, GIF, WEBP, SVG
- Utilizare: Pattern-uri vizuale (Dao, svastica, etc.), screenshots UI, diagrame
- Procesare:
  - OCR dacă conține text
  - Pattern recognition vizual
  - Salvare metadata (hash, dimensiuni, dată)
  - Cross-reference cu patterns din 03_INTELLIGENCE/patterns/

### 2. Audio
- Format: MP3, WAV, OGG, M4A
- Utilizare: Voice notes, înregistrări ritualuri, muzică liturgică
- Procesare:
  - Transcription (speech-to-text)
  - Metadata extraction (durată, sample rate)
  - Pattern recognition audio
  - Salvare transcript + metadata

### 3. Video
- Format: MP4, MOV, AVI, MKV, WEBM
- Utilizare: Sesiuni înregistrate, demonstrații, documentare
- Procesare:
  - Frame extraction (key frames)
  - Audio extraction pentru transcription
  - Metadata extraction
  - Scene detection

### 4. Documente
- Format: PDF, DOCX, XLSX, PPTX, MD, TXT
- Utilizare: Foundation documents, cercetare, specificații
- Procesare:
  - Text extraction
  - Structure parsing
  - Metadata extraction
  - Indexare pentru retrieval

### 5. Web URLs
- Format: HTTP/HTTPS
- Utilizare: Surse externe, R-2 verification, documentare
- Procesare:
  - Fetch HTML
  - Extract main content
  - Extract metadata
  - Salvare locală pentru persistență

## Implementare

### Schelet Python

```python
class MultiModalProcessor:
    """Procesează toate tipurile de input"""

    def __init__(self, workspace):
        self.workspace = workspace
        self.processed_files = []

    def process(self, file_path_or_url):
        """Detectează tipul și procesează"""
        if self.is_url(file_path_or_url):
            return self.process_url(file_path_or_url)
        elif self.is_image(file_path_or_url):
            return self.process_image(file_path_or_url)
        elif self.is_audio(file_path_or_url):
            return self.process_audio(file_path_or_url)
        elif self.is_video(file_path_or_url):
            return self.process_video(file_path_or_url)
        elif self.is_document(file_path_or_url):
            return self.process_document(file_path_or_url)
        else:
            return {'error': 'Unknown format'}

    def process_image(self, path):
        """Procesează imagine"""
        from PIL import Image
        import hashlib

        img = Image.open(path)
        metadata = {
            'path': str(path),
            'format': img.format,
            'size': img.size,
            'mode': img.mode,
            'hash': hashlib.md5(path.read_bytes()).hexdigest(),
            'processed_at': datetime.now().isoformat()
        }

        # Salvează metadata
        self._save_metadata(metadata)

        # Detectează pattern-uri vizuale
        patterns = self._detect_visual_patterns(img)
        metadata['detected_patterns'] = patterns

        return metadata

    def process_audio(self, path):
        """Procesează audio"""
        # Folosește whisper sau alt tool
        metadata = {
            'path': str(path),
            'duration': None,  # calculabil cu ffprobe
            'format': path.suffix,
            'transcription': None,  # placeholder
            'processed_at': datetime.now().isoformat()
        }
        return metadata

    def process_video(self, path):
        """Procesează video"""
        # Folosește ffmpeg pentru metadata + frame extraction
        metadata = {
            'path': str(path),
            'format': path.suffix,
            'duration': None,
            'frames_extracted': 0,
            'processed_at': datetime.now().isoformat()
        }
        return metadata

    def process_document(self, path):
        """Procesează document"""
        metadata = {
            'path': str(path),
            'format': path.suffix,
            'text_extracted': None,
            'structure': None,
            'processed_at': datetime.now().isoformat()
        }

        if path.suffix == '.pdf':
            # pdftotext sau pypdf
            pass
        elif path.suffix == '.docx':
            # python-docx
            pass
        elif path.suffix == '.md' or path.suffix == '.txt':
            metadata['text_extracted'] = path.read_text(encoding='utf-8')

        return metadata

    def process_url(self, url):
        """Procesează URL"""
        import urllib.request
        # fetch content
        return {
            'url': url,
            'fetched_at': datetime.now().isoformat(),
            'content': None  # populated after fetch
        }
```

## Pattern Recognition pentru Imagini

### Pattern: Dao/Yin-Yang
```
Detectează:
- Cerc divizat prin curbă-S
- Două regiuni (dark/light)
- Două puncte (ochi)
- Proporții recognoscibile

Output:
{
    'pattern_type': 'dao_yin_yang',
    'confidence': 0.85,
    'cultural_origin': 'East Asian',
    'complexity': 'high'
}
```

### Pattern: Svastica
```
Detectează:
- 4 brațe la 90 grade
- Fiecare braț se termină perpendicular
- Centru gol sau punct

Output:
{
    'pattern_type': 'swastika',
    'confidence': 0.95,
    'cultural_origin': 'multi-cultural',
    'complexity': 'medium'
}
```

## Salvare și Indexare

```
La procesare:
1. Salvează metadata în 09_LOGS/multimodal_metadata.json
2. Indexează în 03_INTELLIGENCE/patterns/
3. Adaugă în LEARNING_LOG
4. Activează retrieval pentru sesiuni viitoare
```

## Cross-Substrate Compatibility

```
Multi-modal processor e cross-substrate:
- Tools diferite per LLM (vision, audio, etc.)
- Principiile sunt aceleași
- Implementarea specifică variază
```

## Integrare cu R-2

```
La procesare imagine cu claim factual:
1. Salvează imaginea
2. Extrage metadata
3. Pattern recognition
4. R-2 verification (e pattern-ul corect?)
5. Output cu educated guess markers
```

## Limitări Cunoscute

```
- Image recognition depinde de model (vision capability)
- Audio transcription depinde de model (audio capability)
- Video processing e compute-intensive
- Document parsing e specific per format
- Unele formate exotice nu sunt suportate
```

## Metrici

```
- Files processed per sesiune
- Recognition accuracy
- Metadata completeness
- Cross-reference success rate
= Calitatea multi-modal processing
```

---

**Status:** Design complet
**Versiune:** 1.0
**Aplicabil:** Orice sesiune cu input non-text
