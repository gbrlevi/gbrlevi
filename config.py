# -*- coding: utf-8 -*-
"""
=============================================================================
  EDITE APENAS ESTE ARQUIVO PARA MUDAR O CARD.
  Depois rode:  python generate.py   (ou deixe a GitHub Action rodar sozinha)
=============================================================================

Placeholders disponiveis em qualquer valor (sao trocados automaticamente):

  {uptime}      22 years, 9 months, 10 days   (calculado a partir de BIRTHDAY)
  {repos}       numero de repositorios proprios
  {contrib}     repositorios de terceiros em que voce contribuiu
  {stars}       total de stars recebidas
  {followers}   seguidores
  {following}   seguindo
  {commits}     total de commits (inclui contribuicoes privadas)
  {loc}         linhas de codigo liquidas
  {loc_add}     linhas adicionadas
  {loc_del}     linhas removidas
"""

import datetime

# --- quem e voce -------------------------------------------------------------
USER = "gbrlevi"                              # login do GitHub
NICK = "gbrlevi@github"                       # titulo do card
BIRTHDAY = datetime.date(2003, 11, 30)

# Repos que nao devem entrar na contagem de linhas de codigo
LOC_IGNORE_REPOS = []                         # ex: ["gbrlevi/algum-fork-gigante"]
LOC_COUNT_FORKS = True                        # contar forks? normalmente nao

# --- conteudo do card --------------------------------------------------------
# Tipos de linha:
#   ("kv", "Label:", "valor")          linha normal com pontilhado
#   ("gap",)                           linha em branco
#   ("rule", "Titulo")                 divisoria  - Titulo ------------
#   ("stat2", ("A:", "{x}"), ("B:", "{y}"))   duas colunas
#   ("loc", "Lines of Code:")          linha especial com verde/vermelho
ROWS = [
    ("kv", "OS:",               "Arch Linux / Windows 11"),
    ("kv", "Uptime:",           "{uptime}"),
    ("kv", "Host:",             "Exitus"),
    ("kv", "Kernel:",           "Universidade de Fortaleza"),
    ("kv", "IDE/Text.Editor:",  "VSCode, IntelliJ IDEA, Vim"),
    ("gap",),
    ("kv", "Languages.Code:",   "Python, Java, TypeScript, JavaScript, C#"),
    ("kv", "Languages.Real:",   "English, Portugu\u00eas"),
    ("gap",),
    ("kv", "Stack.Cloud:",      "GCP, Oracle Cloud, AWS, Supabase, Vercel, Fly.io"),
    ("gap",),
    ("kv", "Theory.Focus:",   "Deep Learning, ST-GCN, OS Architecture"),
    ("kv", "AI.Domain:",        "Kinematic Pose Dynamics, Real-Time Video Buffers"),
    ("gap",),
    ("kv", "Hobbies.Hardware:", "PC Building, Thinkpad Modding, Audio Gear"),
    ("kv", "Hobbies.Software:", "Linux Ricing, Remote Streaming, Homelab"),
    ("gap",),
    ("rule", "Contact"),
    ("kv", "Email:",            "gbrlevi7@gmail.com"),
    ("kv" , "LinkedIn:",        "linkedin.com/in/gbrlevi"),
    ("gap",),
    ("rule", "GitHub Stats"),
    ("stat2", ("Repos:", "{repos} {{Contributed: {contrib}}}"), ("Stars:", "{stars}")),
    ("stat2", ("Commits:", "{commits}"), ("Followers:", "{followers}")),
    ("loc", "Lines of Code:"),
]

# --- janela de terminal ------------------------------------------------------
TERMINAL_CHROME = True                 # barra de titulo com as tres bolinhas
WINDOW_TITLE = "gbrlevi@github: ~"
PROMPT_USER = "gbrlevi@github"
PROMPT_SIGN = ":~$"
PROMPT_CMD = "neofetch"
SHOW_CURSOR = True                     # cursor piscando no fim

# --- layout ------------------------------------------------------------------
ASCII_FILE = "ascii_art.txt"
TONE_FILE = "ascii_tone.txt"           # opcional; sem ele a arte fica monocromatica
INFO_WIDTH = 63          # largura da coluna de texto, em caracteres
FONT_SIZE = 14.0
LINE_HEIGHT = 19.0
GUTTER_COLS = 59         # onde a coluna de texto comeca (em caracteres)
PAD_LEFT = 22.0
PAD_TOP = 34.0
ANIMATE = True           # fade-in escalonado

FONT_STACK = ("'Cascadia Code','JetBrains Mono','Fira Code','SF Mono',"
              "Consolas,'DejaVu Sans Mono','Courier New',monospace")

# --- paletas -----------------------------------------------------------------
THEMES = {
    "dark": dict(
        bg="#1a1b27", border="#2b2d42", art="#dfe4ec", header="#70a5fd",
        label="#7ce082", value="#a9c9ff", dots="#3c4166", dash="#3c4166",
        sec="#c9d1d9", num="#f0f3f8", add="#3fb950", rem="#f85149",
        # arte: tom 0 (mais escuro) -> tom f (mais claro), e os acentos
        art_low="#333b56", art_high="#f2f6fb",
        art_green="#7ce082", art_teal="#58c8c4",
        # janela
        chrome_bg="#15161f", chrome_line="#2b2d42", chrome_title="#6b7394",
        prompt_sign="#6b7394", prompt_cmd="#7ce082", cursor="#7ce082",
    ),
    "light": dict(
        bg="#ffffff", border="#d0d7de", art="#24292f", header="#0969da",
        label="#bc4c00", value="#0550ae", dots="#d8dee4", dash="#afb8c1",
        sec="#57606a", num="#1f2328", add="#1a7f37", rem="#cf222e",
        art_low="#1a2028", art_high="#aab3c0",
        art_green="#1c8c3c", art_teal="#14828c",
        chrome_bg="#f6f8fa", chrome_line="#d0d7de", chrome_title="#6e7781",
        prompt_sign="#6e7781", prompt_cmd="#1a7f37", cursor="#1a7f37",
    ),
}

OUTPUT = {"dark": "dark_mode.svg", "light": "light_mode.svg"}
