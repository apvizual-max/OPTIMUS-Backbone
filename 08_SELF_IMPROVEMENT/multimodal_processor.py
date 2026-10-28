#!/usr/bin/env python3
"""
Multi-Modal Processor for SENTINEL_PRIME
Real implementations: images, audio (whisper), video, documents (PDF/DOCX/XLSX/PPTX/MD).
All code/comments/messages in English.
"""
import json
import os
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List


WORKSPACE = Path(os.environ.get('WORKSPACE_ROOT', 'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Optimus-Dashboard\\SENTINEL_PRIME'))
METADATA_FILE = WORKSPACE / '09_LOGS' / 'multimodal_metadata.json'


IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.bmp'}
AUDIO_FORMATS = {'.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac'}
VIDEO_FORMATS = {'.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv'}
DOC_FORMATS = {'.pdf', '.docx', '.xlsx', '.pptx', '.md', '.txt', '.rtf'}


class MultiModalProcessor:
    """Process multiple input types with real implementations"""

    def __init__(self, workspace: Path = WORKSPACE):
        self.workspace = workspace
        self.processed = []
        METADATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        if not METADATA_FILE.exists():
            METADATA_FILE.write_text('[]', encoding='utf-8')

    def detect_type(self, path_or_url: str) -> str:
        """
        Detect input type by extension or URL scheme.
        Type detection is syntactic - does not require file existence.
        Existence is verified at process() time.
        """
        if path_or_url.startswith('http://') or path_or_url.startswith('https://'):
            return 'url'
        if path_or_url.startswith('file://') or path_or_url.startswith('data:'):
            return 'url'

        ext = Path(path_or_url).suffix.lower()
        if ext in IMAGE_FORMATS:
            return 'image'
        elif ext in AUDIO_FORMATS:
            return 'audio'
        elif ext in VIDEO_FORMATS:
            return 'video'
        elif ext in DOC_FORMATS:
            return 'document'

        # Unknown extension or no extension
        if not ext:
            return 'unknown'
        return 'unknown'

    def process(self, path_or_url: str) -> Dict:
        """Process according to detected type"""
        input_type = self.detect_type(path_or_url)

        if input_type == 'url':
            return self.process_url(path_or_url)
        elif input_type == 'image':
            return self.process_image(path_or_url)
        elif input_type == 'audio':
            return self.process_audio(path_or_url)
        elif input_type == 'video':
            return self.process_video(path_or_url)
        elif input_type == 'document':
            return self.process_document(path_or_url)
        else:
            return {
                'input': path_or_url,
                'type': 'unknown',
                'status': 'FAILED',
                'message': f'Could not detect type for {path_or_url}'
            }

    def process_image(self, path: str) -> Dict:
        """Process image - extract metadata + dimensions + perceptual hash"""
        p = Path(path)
        metadata = {
            'input': str(p),
            'type': 'image',
            'format': p.suffix.lower(),
            'size_bytes': p.stat().st_size if p.exists() else 0,
            'hash': hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None,
            'processed_at': datetime.now().isoformat(),
            'status': 'OK'
        }

        # PIL extraction
        try:
            from PIL import Image
            img = Image.open(p)
            metadata['dimensions'] = img.size
            metadata['width'] = img.width
            metadata['height'] = img.height
            metadata['mode'] = img.mode
            metadata['has_alpha'] = 'A' in img.mode
            metadata['format_full'] = img.format

            # Perceptual hash for pattern matching
            try:
                phash = self._perceptual_hash(img)
                metadata['perceptual_hash'] = phash
            except Exception as e:
                metadata['perceptual_hash_error'] = str(e)

        except ImportError:
            metadata['pil_error'] = 'PIL not available'
        except Exception as e:
            metadata['image_metadata_error'] = str(e)

        # Pattern detection candidates
        metadata['detected_patterns'] = self._detect_visual_patterns(p)

        self._save_metadata(metadata)
        return metadata

    def process_audio(self, path: str) -> Dict:
        """Process audio - transcribe with faster-whisper"""
        p = Path(path)
        metadata = {
            'input': str(p),
            'type': 'audio',
            'format': p.suffix.lower(),
            'size_bytes': p.stat().st_size if p.exists() else 0,
            'hash': hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None,
            'processed_at': datetime.now().isoformat(),
            'status': 'OK',
            'transcription': None,
            'duration': None,
            'language': None
        }

        if not p.exists():
            metadata['status'] = 'ERROR'
            metadata['error'] = 'File not found'
            self._save_metadata(metadata)
            return metadata

        # Try faster-whisper
        try:
            from faster_whisper import WhisperModel
            # Use base model for speed; can be configured to 'small', 'medium', 'large-v3'
            model = WhisperModel('base', device='cpu', compute_type='int8')

            segments, info = model.transcribe(str(p), beam_size=5)

            transcription_parts = []
            for segment in segments:
                transcription_parts.append(segment.text)

            metadata['transcription'] = ' '.join(transcription_parts).strip()
            metadata['language'] = info.language
            metadata['language_probability'] = info.language_probability
            metadata['duration'] = info.duration
            metadata['whisper_model'] = 'base'

        except ImportError:
            metadata['status'] = 'PARTIAL'
            metadata['error'] = 'faster-whisper not installed - transcription unavailable'
            metadata['note'] = 'pip install faster-whisper to enable'
        except Exception as e:
            metadata['status'] = 'ERROR'
            metadata['error'] = f'Whisper transcription failed: {e}'

        self._save_metadata(metadata)
        return metadata

    def process_video(self, path: str) -> Dict:
        """Process video - extract frames + audio transcription"""
        p = Path(path)
        metadata = {
            'input': str(p),
            'type': 'video',
            'format': p.suffix.lower(),
            'size_bytes': p.stat().st_size if p.exists() else 0,
            'hash': hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None,
            'processed_at': datetime.now().isoformat(),
            'status': 'OK',
            'duration': None,
            'fps': None,
            'frames_extracted': 0,
            'audio_transcription': None
        }

        if not p.exists():
            metadata['status'] = 'ERROR'
            metadata['error'] = 'File not found'
            self._save_metadata(metadata)
            return metadata

        # Try OpenCV for frame extraction
        try:
            import cv2
            cap = cv2.VideoCapture(str(p))
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                duration = frame_count / fps if fps > 0 else 0

                metadata['fps'] = fps
                metadata['frame_count'] = frame_count
                metadata['width'] = width
                metadata['height'] = height
                metadata['duration'] = duration

                # Extract frames at 1fps for analysis
                frames_dir = WORKSPACE / '09_LOGS' / 'video_frames'
                frames_dir.mkdir(parents=True, exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                safe_name = p.stem.replace(' ', '_')

                frame_count_extracted = 0
                max_frames = 30
                frame_interval = max(1, int(fps)) if fps > 0 else 30

                for frame_idx in range(0, min(frame_count, max_frames * frame_interval), frame_interval):
                    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                    ret, frame = cap.read()
                    if ret:
                        frame_path = frames_dir / f"{safe_name}_{timestamp}_frame{frame_count_extracted:03d}.jpg"
                        cv2.imwrite(str(frame_path), frame)
                        frame_count_extracted += 1

                metadata['frames_extracted'] = frame_count_extracted
                metadata['frames_dir'] = str(frames_dir)
            else:
                metadata['status'] = 'ERROR'
                metadata['error'] = 'Could not open video file'
            cap.release()
        except ImportError:
            metadata['status'] = 'PARTIAL'
            metadata['error'] = 'opencv-python not installed'
            metadata['note'] = 'pip install opencv-python to enable frame extraction'
        except Exception as e:
            metadata['status'] = 'ERROR'
            metadata['error'] = f'Video processing failed: {e}'

        self._save_metadata(metadata)
        return metadata

    def process_document(self, path: str) -> Dict:
        """Process document - real text extraction per format"""
        p = Path(path)
        metadata = {
            'input': str(p),
            'type': 'document',
            'format': p.suffix.lower(),
            'size_bytes': p.stat().st_size if p.exists() else 0,
            'hash': hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None,
            'processed_at': datetime.now().isoformat(),
            'status': 'OK',
            'text_extracted': None,
            'text_length': 0,
            'structure': None
        }

        if not p.exists():
            metadata['status'] = 'ERROR'
            metadata['error'] = 'File not found'
            self._save_metadata(metadata)
            return metadata

        ext = p.suffix.lower()

        # MD / TXT - direct read
        if ext in {'.md', '.txt', '.rtf'}:
            try:
                metadata['text_extracted'] = p.read_text(encoding='utf-8')
                metadata['text_length'] = len(metadata['text_extracted'])
            except UnicodeDecodeError:
                try:
                    metadata['text_extracted'] = p.read_text(encoding='cp1252')
                    metadata['text_length'] = len(metadata['text_extracted'])
                    metadata['encoding_used'] = 'cp1252'
                except Exception as e:
                    metadata['status'] = 'ERROR'
                    metadata['error'] = f'Encoding error: {e}'

        # PDF - use pypdf
        elif ext == '.pdf':
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(p))
                text_parts = []
                for page in reader.pages:
                    try:
                        text_parts.append(page.extract_text())
                    except Exception:
                        pass
                metadata['text_extracted'] = '\n'.join(text_parts)
                metadata['text_length'] = len(metadata['text_extracted'])
                metadata['page_count'] = len(reader.pages)
                metadata['structure'] = {'pages': len(reader.pages)}
            except ImportError:
                metadata['status'] = 'ERROR'
                metadata['error'] = 'pypdf not installed'
            except Exception as e:
                metadata['status'] = 'ERROR'
                metadata['error'] = f'PDF extraction failed: {e}'

        # DOCX - use python-docx
        elif ext == '.docx':
            try:
                from docx import Document
                doc = Document(str(p))
                text_parts = [para.text for para in doc.paragraphs]
                metadata['text_extracted'] = '\n'.join(text_parts)
                metadata['text_length'] = len(metadata['text_extracted'])
                metadata['paragraph_count'] = len(doc.paragraphs)
                metadata['structure'] = {
                    'paragraphs': len(doc.paragraphs),
                    'tables': len(doc.tables),
                    'sections': len(doc.sections)
                }
            except ImportError:
                metadata['status'] = 'ERROR'
                metadata['error'] = 'python-docx not installed'
            except Exception as e:
                metadata['status'] = 'ERROR'
                metadata['error'] = f'DOCX extraction failed: {e}'

        # XLSX - use openpyxl
        elif ext == '.xlsx':
            try:
                from openpyxl import load_workbook
                wb = load_workbook(str(p), data_only=True, read_only=True)
                text_parts = []
                for sheet_name in wb.sheetnames:
                    sheet = wb[sheet_name]
                    text_parts.append(f'--- Sheet: {sheet_name} ---')
                    for row in sheet.iter_rows(values_only=True, max_row=1000):
                        row_str = ' | '.join(str(c) if c is not None else '' for c in row)
                        if row_str.strip():
                            text_parts.append(row_str)
                metadata['text_extracted'] = '\n'.join(text_parts)
                metadata['text_length'] = len(metadata['text_extracted'])
                metadata['sheet_count'] = len(wb.sheetnames)
                metadata['structure'] = {'sheets': wb.sheetnames}
                wb.close()
            except ImportError:
                metadata['status'] = 'ERROR'
                metadata['error'] = 'openpyxl not installed'
            except Exception as e:
                metadata['status'] = 'ERROR'
                metadata['error'] = f'XLSX extraction failed: {e}'

        # PPTX - use python-pptx
        elif ext == '.pptx':
            try:
                from pptx import Presentation
                prs = Presentation(str(p))
                text_parts = []
                for slide_idx, slide in enumerate(prs.slides):
                    text_parts.append(f'--- Slide {slide_idx + 1} ---')
                    for shape in slide.shapes:
                        if hasattr(shape, 'text'):
                            text_parts.append(shape.text)
                metadata['text_extracted'] = '\n'.join(text_parts)
                metadata['text_length'] = len(metadata['text_extracted'])
                metadata['slide_count'] = len(prs.slides)
                metadata['structure'] = {'slides': len(prs.slides)}
            except ImportError:
                metadata['status'] = 'ERROR'
                metadata['error'] = 'python-pptx not installed'
            except Exception as e:
                metadata['status'] = 'ERROR'
                metadata['error'] = f'PPTX extraction failed: {e}'

        self._save_metadata(metadata)
        return metadata

    def process_url(self, url: str) -> Dict:
        """Process URL - fetch metadata + content type"""
        import urllib.request
        metadata = {
            'input': url,
            'type': 'url',
            'url': url,
            'processed_at': datetime.now().isoformat(),
            'status': 'PENDING',
            'content': None,
            'content_type': None,
            'http_code': None
        }

        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'SENTINEL_PRIME/1.0'}
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read()
                metadata['status'] = 'OK'
                metadata['http_code'] = response.status
                metadata['content_type'] = response.headers.get('Content-Type', '')
                metadata['content_length'] = len(content)

                # Save content preview
                metadata['content_preview'] = content[:500].decode('utf-8', errors='ignore')

        except Exception as e:
            metadata['status'] = 'FAILED'
            metadata['error'] = str(e)

        self._save_metadata(metadata)
        return metadata

    def _perceptual_hash(self, img) -> str:
        """Generate perceptual hash for image (8x8 average hash)"""
        # Resize to 8x8 grayscale
        img_small = img.resize((8, 8)).convert('L')
        pixels = list(img_small.getdata())
        avg = sum(pixels) / len(pixels)

        # Generate bits
        bits = ''.join('1' if p > avg else '0' for p in pixels)

        # Convert to hex
        return hex(int(bits, 2))

    def _detect_visual_patterns(self, image_path: Path) -> List[Dict]:
        """Detect visual pattern candidates via OCR (if pytesseract available)"""
        patterns = []

        # Try OCR for text extraction from image
        try:
            import pytesseract
            from PIL import Image

            # pytesseract resolves tesseract through PATH, which is unreliable
            # for a process that inherited a stale environment. Point it at the
            # resolved binary first, so "not on PATH" cannot masquerade as
            # "OCR unavailable" when the engine is installed and working.
            try:
                import tool_resolver
                resolved = tool_resolver.configure_pytesseract()
                if not resolved.get('found'):
                    patterns.append({
                        'type': 'ocr_engine_missing',
                        'note': f'tesseract engine not found. Tried: '
                                f'{"; ".join(resolved.get("searched", []))}'
                    })
            except ImportError:
                pass  # resolver absent - fall back to pytesseract's own default

            img = Image.open(image_path)
            ocr_text = pytesseract.image_to_string(img)
            if ocr_text.strip():
                patterns.append({
                    'type': 'ocr_text',
                    'value': ocr_text[:500],
                    'note': f'Extracted via pytesseract, length: {len(ocr_text)}'
                })
        except ImportError:
            patterns.append({
                'type': 'ocr_unavailable',
                'note': 'pytesseract not installed - install to enable OCR'
            })
        except Exception as e:
            patterns.append({
                'type': 'ocr_error',
                'note': str(e)
            })

        # Hash for matching
        try:
            if image_path.exists():
                file_hash = hashlib.md5(image_path.read_bytes()).hexdigest()
                patterns.append({
                    'type': 'hash',
                    'value': file_hash,
                    'note': 'Use hash for matching with known patterns in 03_INTELLIGENCE/patterns/'
                })
        except Exception:
            pass

        return patterns

    def _save_metadata(self, metadata: Dict):
        """Save metadata to file"""
        try:
            current = json.loads(METADATA_FILE.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, FileNotFoundError):
            current = []

        current.append(metadata)

        # Keep last 1000 entries
        if len(current) > 1000:
            current = current[-1000:]

        METADATA_FILE.write_text(
            json.dumps(current, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )

        self.processed.append(metadata)

    def get_processed_history(self) -> List[Dict]:
        """Return processing history"""
        return self.processed.copy()


def main():
    """Demo: multi-modal processor"""
    processor = MultiModalProcessor()

    print("=" * 60)
    print("SENTINEL Multi-Modal Processor Demo")
    print("=" * 60)

    # Test inputs - all real files that exist in workspace
    test_inputs = [
        'C:\\Users\\apviz\\.minimax-agent\\projects\\Mavis-Optimus-Dashboard\\SENTINEL_PRIME\\01_FOUNDATION\\doctrine\\A_FI_DOCTRINE.md',  # doc
        'https://en.wikipedia.org/wiki/Cucuteni%E2%80%93Trypillia_culture',  # URL
        'test.png',  # test type detection (synthetic, doesn't exist)
        'test.mp3',
        'test.pdf',
    ]

    for inp in test_inputs:
        input_type = processor.detect_type(inp)
        print(f"\n[INPUT] {inp}")
        print(f"[TYPE] {input_type}")

        if Path(inp).exists() or input_type == 'url':
            result = processor.process(inp)
            print(f"[STATUS] {result.get('status')}")
            if 'text_length' in result:
                print(f"[TEXT_LENGTH] {result['text_length']}")
            if 'size_bytes' in result and result['size_bytes']:
                print(f"[SIZE] {result['size_bytes']} bytes")
            if 'format' in result:
                print(f"[FORMAT] {result['format']}")
        else:
            print(f"[SKIP] File does not exist (type detection only)")

    # --- image + OCR, demonstrated rather than assumed --------------------
    # The demo previously only walked a markdown file and a URL, so OCR was
    # installed but never visible. A capability nobody can see is a claim, not
    # a capability. This renders a known string and reads it back, so the
    # printed text is measured output of the real engine - and a failure here
    # says so rather than printing a success line.
    print("\n" + "=" * 60)
    print("Image + OCR demonstration")
    print("=" * 60)
    fixture_dir = WORKSPACE / '09_LOGS' / 'multimodal_demo'
    fixture_dir.mkdir(parents=True, exist_ok=True)
    fixture = fixture_dir / 'ocr_probe.png'
    expected = 'SENTINEL 42'
    try:
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (900, 160), 'white')
        draw = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype('arial.ttf', 96)
        except OSError:
            font = ImageFont.load_default(size=96)
        draw.text((30, 25), expected, fill='black', font=font)
        img.save(fixture)
        print(f"[FIXTURE] {fixture} ({fixture.stat().st_size} bytes, text={expected!r})")

        result = processor.process(str(fixture))
        print(f"[STATUS] {result.get('status')}")
        print(f"[DIMS] {result.get('width')}x{result.get('height')} {result.get('mode')}")
        for pattern in result.get('detected_patterns', []):
            kind = pattern.get('type')
            if kind == 'ocr_text':
                read_back = ' '.join(str(pattern.get('value', '')).split())
                print(f"[OCR] read: {read_back!r}")
                print(f"[OCR] expected: {expected!r}")
                print(f"[OCR] match: {expected in read_back}")
            elif kind in ('ocr_unavailable', 'ocr_error', 'ocr_engine_missing'):
                print(f"[OCR] NOT AVAILABLE: {pattern.get('note')}")
    except ImportError as exc:
        print(f"[SKIP] image fixture needs Pillow: {exc}")

    # Show history
    history = processor.get_processed_history()
    print(f"\nProcessed in this session: {len(history)}")


if __name__ == '__main__':
    main()
