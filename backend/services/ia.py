from __future__ import annotations

import subprocess
import re
import json
from pathlib import Path
from typing import Dict

try:
    import demjson3  # pip install demjson3
    _HAS_DEMJSON = True
except ImportError:
    _HAS_DEMJSON = False


# ─────────────────────────────────────────────────────
# ✏️  ADAPTER CES CHEMINS À TON ENVIRONNEMENT
# ─────────────────────────────────────────────────────
LLAMA_BIN = Path(
    r"C:\Users\Moi\Desktop\doc polytech\doc niveau 4 - AIA 4\S2\Geni logiciel"
    r"\Projet\implementation\backend\llama.cpp-master\build\bin\Release\llama-run.exe"
)
MODEL_PATH = Path(
    r"C:\Users\Moi\Desktop\doc polytech\doc niveau 4 - AIA 4\S2\Geni logiciel"
    r"\Projet\implementation\backend\llama.cpp-master\models\tinyllama-1.1b-chat-v1.0.Q4_0.gguf"
)
N_THREADS = "6"
TEMPERATURE = "0.7"


# ─────────────────────────────────────────────────────
#  Lance llama.cpp en local
# ─────────────────────────────────────────────────────
def _run_llama(prompt: str, max_tokens: int = 512) -> str:
    if not LLAMA_BIN.exists():
        raise FileNotFoundError(f"llama-run introuvable : {LLAMA_BIN}")
    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"Modèle GGUF introuvable : {MODEL_PATH}")

    cmd = [
        str(LLAMA_BIN),
        str(MODEL_PATH),
        "--threads", N_THREADS,
        "--temp", TEMPERATURE,
        prompt
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


# ─────────────────────────────────────────────────────
#  Extrait proprement le JSON depuis la réponse
# ─────────────────────────────────────────────────────
def _extract_last_json(text: str) -> str:
    matches = list(re.finditer(r"\{[\s\S]*?\}", text))
    if not matches:
        raise ValueError("Aucun JSON détecté dans la réponse du modèle")

    blob = matches[-1].group()
    blob = re.sub(r",\s*}", "}", blob)
    blob = re.sub(r",\s*]", "]", blob)
    return blob


# ─────────────────────────────────────────────────────
# Génère un plan de repas (structure brute)
# ─────────────────────────────────────────────────────
def generer_structure_plan(contraintes_utilisateur: str, jours: int = 3) -> Dict:
    prompt = (
        "Tu es un nutritionniste professionnel.\n"
        f"Génère un plan de repas de {jours} jour(s), avec matin / midi / soir.\n"
        "Retourne UNIQUEMENT un objet JSON strict (aucun commentaire ni texte) :\n"
        "{\n"
        '  "jour_1": {"matin": "...", "midi": "...", "soir": "..."},\n'
        '  "jour_2": {...},\n'
        f'  "jour_{jours}": {{...}}\n'
        "}\n"
        f"\nContrainte utilisateur : {contraintes_utilisateur}.\n"
        "Évite les desserts, fritures, produits transformés, sucre raffiné."
    )

    raw = _run_llama(prompt, max_tokens=800)
    print("\n===== RÉPONSE BRUTE IA =====\n", raw, "\n=============================\n")

    json_str = _extract_last_json(raw)

    if _HAS_DEMJSON:
        structure = demjson3.decode(json_str)
        return {"json": structure}
    else:
        return {"texte_ia": json_str}


# ─────────────────────────────────────────────────────
# Génère une recette complète à partir d’un titre
# ─────────────────────────────────────────────────────
def generer_recette_detaillee(intent: str) -> Dict:
    prompt = (
        f"Génère une recette complète pour : {intent}\n"
        "Retourne uniquement ce JSON strict :\n"
        '{\n'
        '  "titre": "Nom de la recette",\n'
        '  "description": "Courte description",\n'
        '  "ingredients": ["ingrédient 1", "ingrédient 2"],\n'
        '  "instructions": "Étapes détaillées pour cuisiner"\n'
        '}'
    )

    raw = _run_llama(prompt, max_tokens=700)
    print("\n===== RECETTE IA BRUTE =====\n", raw, "\n=============================\n")

    json_str = _extract_last_json(raw)

    if _HAS_DEMJSON:
        recette = demjson3.decode(json_str)
        return {"json": recette}
    else:
        return {"texte_ia": json_str}
