"""Quick command processor — detects and executes simple commands without Jarvis overhead."""

import re
import logging

logger = logging.getLogger(__name__)

# Simple command keywords that trigger fast execution
SIMPLE_COMMAND_KEYWORDS = {
    "abrir", "abre", "abra",  # open
    "fechar", "fecha", "fechem",      # close
    "tocar", "toca", "tocarem",       # play
    "pausar", "pausa",                # pause
    "parar", "para",                  # stop
    "volume", "som",                  # volume/sound
    "ligar", "liga",                  # turn on
    "desligar", "desliga",            # turn off
}

# Application keywords to recognize
APP_KEYWORDS = {
    "spotify": "Spotify",
    "youtube": "YouTube",
    "netflix": "Netflix",
    "apple": "Apple Music",
    "música": "Music",
    "música": "Music",
    "chrome": "Chrome",
    "firefox": "Firefox",
    "safari": "Safari",
    "vscode": "VS Code",
    "terminal": "Terminal",
    "finder": "Finder",
}


def palavras_parecidas(p1: str, p2: str) -> bool:
    """Check if two words are similar enough to be considered matches.
    
    Uses simple similarity metrics to tolerate typos.
    
    Args:
        p1: First word
        p2: Second word
        
    Returns:
        True if words are similar enough
    """
    p1 = p1.lower()
    p2 = p2.lower()

    # Mesmo comprimento ou diferença de no máximo 2 caracteres
    len_diff = abs(len(p1) - len(p2))
    if len_diff > 2:
        return False

    # Match direto (uma palavra contém a outra completamente)
    if p1 == p2:
        return True
    
    # Para palavras curtas, exigir match quase exato
    if len(p1) <= 4 or len(p2) <= 4:
        # Diferença de apenas 1 caracter
        if len_diff == 1:
            # Verificar se uma é prefixo da outra
            return p1.startswith(p2) or p2.startswith(p1) or p1.endswith(p2) or p2.endswith(p1)
        return False

    # Similaridade por letras em comum
    matches = sum(1 for c in p1 if c in p2)
    
    # Se mais da metade das letras baterem
    return matches >= max(len(p1), len(p2)) * 0.7


def processar_comando(command: str) -> str:
    """Process command by removing Lena prefix and converting to lowercase.
    
    Args:
        command: Raw command from user
        
    Returns:
        Cleaned command string
    """
    # Convert to lowercase
    cmd = command.strip().lower()
    
    # Remove "lena" variants from the beginning
    patterns = [
        r"^oi\s+lena\s+",  # "oi lena ..."
        r"^lena\s+",        # "lena ..."
        r"^ei\s+lena\s+",   # "ei lena ..."
        r"^oi\s+",          # "oi ..."
    ]
    
    for pattern in patterns:
        cmd = re.sub(pattern, "", cmd)
    
    return cmd.strip()


def eh_comando_simples(command: str) -> bool:
    """Check if command is a simple command that can be executed immediately.
    
    REQUIRES BOTH:
    - An action (abrir, fechar, tocar, etc)
    - An application or target (spotify, chrome, etc) - tolerates typos
    
    Args:
        command: Already processed command (lowercase, without "lena" prefix)
        
    Returns:
        True if command is simple AND has an app, False otherwise
    """
    # Split command into words for more precise matching
    palavras = command.split()
    
    # Check if command contains any simple command keywords
    tem_acao = any(keyword in palavras for keyword in SIMPLE_COMMAND_KEYWORDS)
    
    # Check if command contains any known app (with typo tolerance)
    tem_app = False
    for palavra in palavras:
        for app_key in APP_KEYWORDS.keys():
            if palavras_parecidas(palavra, app_key):
                tem_app = True
                break
        if tem_app:
            break
    
    # Only return True if BOTH action and app are present
    return tem_acao and tem_app


def executar_comando_simples(command: str) -> str:
    """Execute a simple command and return quick response.
    
    Args:
        command: Already processed command
        
    Returns:
        Quick response text
    """
    cmd = command.strip().lower()
    
    # Extract app name if present (with typo tolerance)
    app_name = None
    palavras = cmd.split()
    
    # Encontrar o melhor match (mais letras em comum)
    best_match_score = 0
    best_app_display = None
    
    for palavra in palavras:
        for app_key, app_display in APP_KEYWORDS.items():
            if palavras_parecidas(palavra, app_key):
                # Calcular score de similaridade (letras em comum)
                matches = sum(1 for c in palavra.lower() if c in app_key.lower())
                score = matches / max(len(palavra), len(app_key))
                
                if score > best_match_score:
                    best_match_score = score
                    best_app_display = app_display
    
    if best_app_display:
        app_name = best_app_display
    
    # Determine action
    action = None
    responses = {
        "abrir": "Abrindo",
        "abre": "Abrindo",
        "abra": "Abrindo",
        "fechar": "Fechando",
        "fecha": "Fechando",
        "tocar": "Tocando",
        "toca": "Tocando",
        "pausar": "Pausando",
        "pausa": "Pausando",
        "parar": "Parando",
        "para": "Parando",
        "ligar": "Ligando",
        "liga": "Ligando",
        "desligar": "Desligando",
        "desliga": "Desligando",
    }
    
    for key, response_verb in responses.items():
        if key in cmd:
            action = response_verb
            break
    
    # Build response
    if app_name and action:
        logger.info(f"Executing simple command: {action} {app_name}")
        return f"{action} {app_name}..."
    elif action:
        logger.info(f"Executing simple command: {action}")
        return f"{action}..."
    
    return "Comando entendido"


def processar_com_deteccao(
    command: str,
    jarvis_callback,
    use_jarvis_if_not_fast: bool = True,
) -> tuple[str, bool]:
    """Main entry point — routes command to fast execution or Jarvis.
    
    Args:
        command: Raw command from user
        jarvis_callback: Function to call if command needs Jarvis (should return response)
        use_jarvis_if_not_fast: Whether to call Jarvis when command is not simple
        
    Returns:
        Tuple of (response text, is_fast_path)
    """
    # Process command
    cmd_processado = processar_comando(command)
    normalized = cmd_processado.strip().lower()

    # Fast reply for greetings
    saudacoes = ["oi", "olá", "ola", "e aí", "eaí", "opa"]
    if normalized in saudacoes:
        return "Oi! Como posso te ajudar?", True

    # Check if it's a simple command
    if eh_comando_simples(cmd_processado):
        response = executar_comando_simples(cmd_processado)
        logger.info(f"Fast response: {response}")
        return response, True

    if use_jarvis_if_not_fast:
        logger.info(f"Using Jarvis for: {cmd_processado}")
        return jarvis_callback(command), False

    return "", False
