<div align="center">

# Ultimate Best Seller Studio

**Trasforma un'idea in un libro pronto alla pubblicazione — e dimostra che la prosa è umana, non limitarti a sperarlo.**

[![Licenza: MIT](https://img.shields.io/badge/Licenza-MIT-yellow?style=flat-square)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Gira%20su-Claude%20Code%20%2B%20Codex-blueviolet?style=flat-square)](https://claude.ai/code)
[![Human-Band Gate](https://img.shields.io/badge/Human--Band%20Gate-misurato-brightgreen?style=flat-square)](docs/humanizer-pro-integration.md)

*Lingue: [English](README.md) · Italiano · [Português](README.pt-BR.md)*

</div>

---

Hai un'idea. La scrivi. Otto agenti AI studiano il genere, forgiano una premessa con un
motore di ironia strutturale, scrivono ogni capitolo, lo valutano in modo indipendente,
revisionano tutto ciò che sta sotto la soglia e impacchettano il risultato per la
pubblicazione.

Questo è un fork di [**best-seller-studio**](https://github.com/felipelobomotta-blip/best-seller-studio)
di Felipe Lobo (MIT), con una grande idea in più e il motore affilato attorno a essa:

> **Un libro non deve solo *ottenere un buon punteggio* — la sua prosa deve stare dentro
> la reale distribuzione umana, e ora questo si misura, non si va a sensazione.**

La misura arriva da **[Better Humanizer](https://github.com/jodyjdc/better-humanizer)**,
collegato qui come unica fonte di verità (un sottomodulo git) e integrato nella pipeline
come nuovo gate quantitativo.

---

## Cosa cambia rispetto a best-seller-studio

| | best-seller-studio | **Ultimate Best Seller Studio** |
|---|---|---|
| Passaggio de-AI | `humanizer` a regole (checklist statica) | **Better Humanizer** (`humanizer-pro`): misurato, consapevole del registro, anti-ipercorrezione |
| Umanità della prosa | solo qualitativa | **human-band gate misurato** — distanza stilometrica riproducibile per capitolo |
| Packaging | script, nessun install | `pyproject.toml` + comando `ubss` |
| Controllo stato | — | self-check `ubss doctor` |
| Output CLI | testo | testo **o `--json`** su ogni comando di lettura |
| CI | nessuna | GitHub Actions (3.11–3.13) + ruff |
| Dipendenze runtime | stdlib | stdlib (invariato — gira ovunque ci sia Python 3) |

Tutto ciò che l'upstream faceva bene resta: pipeline su file, agenti, Genesis Score
e corpora di conoscenza.

## Compatibilità

**Pensato prima di tutto per [Claude Code](https://claude.ai/code)** (skill + agenti nativi,
slash command `/book-genesis-core`, `/humanizer-pro`). **Gira anche su qualsiasi agente che
legge file** — Codex, Antigravity, Kimi — puntandolo a [`AGENTS.md`](AGENTS.md). Il runner
Python e lo scoring (`stylo.py`) danno gli **stessi numeri ovunque**: il gate di banda umana è
riproducibile bit-per-bit. Cambia solo il modello che scrive il testo.

---

## Avvio rapido

```bash
# 1. Clona con il sottomodulo Better Humanizer
git clone --recurse-submodules https://github.com/jodyjdc/ultimate-best-seller-studio
cd ultimate-best-seller-studio
git submodule update --init --recursive   # se hai già clonato senza --recurse-submodules

# 2. Installa skill + agenti in Claude Code (e il Better Humanizer completo)
./install.sh            # macOS / Linux   (install.ps1 su Windows)

# 3. Verifica che tutto sia pronto
python3 -m runner.cli doctor

# 4. In Claude Code:
#    "Ho un'idea per un libro: [la tua idea]"
```

---

## Due gate, non uno

1. **Genesis Score (qualitativo)** — un agente valutatore separato, che non ha scritto il
   capitolo, lo giudica su una rubrica a 7 dimensioni con il *principio del pavimento* (il
   libro vale quanto la sua dimensione più debole), più una scansione anti-AI a 20 pattern.
2. **Human-Band Gate (misurato) · nuovo** —

```bash
ubss humanize-score <progetto>           # valuta ogni capitolo, scrive un report
ubss humanize-score <progetto> --gate    # esce con errore se un capitolo è segnalato
```

Lo scorer di [Better Humanizer](https://github.com/jodyjdc/better-humanizer) misura la
**distanza stilometrica dalla reale distribuzione umana** per il registro `literary`.
Segnala sia i "tell" dell'AI sia l'ipercorrezione (un capitolo levigato troppo è esso
stesso un segnale). Dettagli in [docs/humanizer-pro-integration.md](docs/humanizer-pro-integration.md).

---

## Better Humanizer, collegato non copiato

Il cervello de-AI è un progetto a sé, incluso come sottomodulo git con versione fissata,
così non va mantenuto in due posti:

```bash
git submodule update --remote   # aggiorna all'ultimo Better Humanizer
```

- Upstream: <https://github.com/jodyjdc/better-humanizer>
- Qui: `external/better-humanizer/` + la giunzione sottile (`skills/humanizer-pro/`,
  `runner/humanband.py`, `ubss humanize-score`).

---

## Avvertenze oneste

- **Non è una garanzia di bestseller letterale.** Copertina, marketing, tempismo e fortuna
  stanno fuori dal manoscritto.
- **La soglia di distanza human-band è un'euristica editoriale regolabile**, non il punteggio
  di un rilevatore di AI; battere i rilevatori commerciali è un non-obiettivo esplicito. I
  numeri sono riproducibili, la soglia è un giudizio. Usala *insieme* a una lettura umana,
  non al suo posto.

---

## Crediti e licenza

Licenza MIT. Fork di [**best-seller-studio**](https://github.com/felipelobomotta-blip/best-seller-studio)
di [Felipe Lobo](https://github.com/felipelobomotta-blip); copyright originale mantenuto in
`LICENSE`, attribuzione completa in [`NOTICE.md`](NOTICE.md). Integrazione di Better
Humanizer e i miglioramenti sopra © 2026 Jody Cecchetto.
