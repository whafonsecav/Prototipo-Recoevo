# Transcripción en español con Whisper-small (caché de ClonacionVoz) para verificar cada toma de la voz.
# El tokenizador de transformers 5.2 + tokenizers 0.22 de tts-env no convierte los tokens especiales de Whisper, así que
# el prefijo del decodificador se arma con los ids estándar del Whisper multilingüe y el texto se decodifica con vocab.json.
import os
import glob
import json
os.environ.setdefault('HF_HOME', r'C:\Users\willi\ClonacionVoz\modelos\hf')
os.environ.setdefault('HF_HUB_OFFLINE', '1')
import numpy as np
import torch
import torchaudio

PREFIJO = [50258, 50262, 50359, 50363]        # <|startoftranscript|> <|es|> <|transcribe|> <|notimestamps|>
_M = {}


def _bytes_a_unicode():
    bs = list(range(ord('!'), ord('~') + 1)) + list(range(ord('¡'), ord('¬') + 1)) + list(range(ord('®'), ord('ÿ') + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))


def cargar(dev='cuda'):
    if not _M:
        from transformers import WhisperFeatureExtractor, WhisperForConditionalGeneration
        fe = WhisperFeatureExtractor.from_pretrained('openai/whisper-small')
        mod = WhisperForConditionalGeneration.from_pretrained('openai/whisper-small').to(dev).eval()
        snap = glob.glob(os.path.join(r'C:\Users\willi\ClonacionVoz\modelos\whisper', 'models--mobiuslabsgmbh--faster-whisper-large-v3-turbo',
                                      'snapshots', '*', 'tokenizer.json'))[0]   # misma tabla BPE de texto que whisper-small
        vocab = {v: k for k, v in json.load(open(snap, encoding='utf-8'))['model']['vocab'].items()}
        _M.update(fe=fe, mod=mod, dev=dev, vocab=vocab, b=({v: k for k, v in _bytes_a_unicode().items()}))
    return _M


def decodificar(ids):
    m = _M
    txt = ''.join(m['vocab'].get(i, '') for i in ids if i < 50257)
    return bytearray(m['b'][c] for c in txt if c in m['b']).decode('utf-8', 'replace').strip()


def transcribir(wav, sr):
    m = cargar('cuda' if torch.cuda.is_available() else 'cpu')
    x = torch.from_numpy(np.asarray(wav, dtype=np.float32))
    if sr != 16000:
        x = torchaudio.functional.resample(x, sr, 16000)
    feats = m['fe'](x.numpy(), sampling_rate=16000, return_tensors='pt').input_features.to(m['dev'])
    with torch.no_grad():
        out = m['mod'].generate(feats, decoder_input_ids=torch.tensor([PREFIJO], device=m['dev']), max_new_tokens=200)
    return decodificar(out[0].tolist())          # los tokens especiales se descartan al decodificar


if __name__ == '__main__':
    import sys
    import soundfile as sf
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from voz_omnivoice import wer
    guion = {b['id']: b for b in json.load(open(sys.argv[1], encoding='utf-8'))}
    carpeta = sys.argv[2]
    for bid, b in guion.items():
        w, s = sf.read(os.path.join(carpeta, bid + '.wav'), dtype='float32')
        t = transcribir(w, s)
        print(f"{bid}\t{wer(b['voz'], t):.2f}\t{t}", flush=True)
