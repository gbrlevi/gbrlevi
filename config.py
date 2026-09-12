import datetime

USER = "gbrlevi"                              
NICK = "gbrlevi@github"                       
BIRTHDAY = datetime.date(2003, 11, 30)

# Repos que nao devem entrar na contagem de linhas de codigo
LOC_IGNORE_REPOS = []
LOC_COUNT_FORKS = True

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
    ("kv", "Shell:",            "zsh 5.9 / bash"),
    ("kv", "IDE/Text.Editor:",  "VSCode, IntelliJ IDEA, Vim"),
    ("gap",),
    ("kv", "Languages.Code:",   "Python, Java, TypeScript, JavaScript, C#"),
    ("kv", "Languages.Computer:",  "SQL, Git, Shellscripts, LaTeX"),
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

# --- layout ------------------------------------------------------------------
ASCII_FILE = "ascii_art.txt"
INFO_WIDTH = 63          # largura da coluna de texto, em caracteres
FONT_SIZE = 14.0
LINE_HEIGHT = 19.0
GUTTER_COLS = 55         # onde a coluna de texto comeca (em caracteres)
PAD_LEFT = 22.0
PAD_TOP = 34.0
ANIMATE = True           # fade-in escalonado

FONT_STACK = ("'Cascadia Code','JetBrains Mono','Fira Code','SF Mono',"
              "Consolas,'DejaVu Sans Mono','Courier New',monospace")

# --- paletas -----------------------------------------------------------------
THEMES = {
    "dark": dict(
        bg="#1a1b27", border="#2b2d42", art="#dfe4ec", header="#70a5fd",
        label="#e8a05c", value="#a9c9ff", dots="#3c4166", dash="#3c4166",
        sec="#c9d1d9", num="#f0f3f8", add="#3fb950", rem="#f85149",
    ),
    "light": dict(
        bg="#ffffff", border="#d0d7de", art="#24292f", header="#0969da",
        label="#bc4c00", value="#0550ae", dots="#d8dee4", dash="#afb8c1",
        sec="#57606a", num="#1f2328", add="#1a7f37", rem="#cf222e",
    ),
}

OUTPUT = {"dark": "dark_mode.svg", "light": "light_mode.svg"}
