from PIL import Image, ImageDraw, ImageFont
import textwrap
import io
import os

# --- FUNÇÕES AUXILIARES ---

def gerarNomeArquivo(nome_completo):
    """Gera um nome de arquivo simplificado a partir de um nome completo."""
    partes = nome_completo.split(" ")
    if not partes:
        return "certificado.pdf"
    
    iniciais = "".join([p[0] for p in partes if p]).upper()
    nome_arquivo = f"{partes[0].lower()}_{iniciais}.pdf"
    return nome_arquivo

# --- FUNÇÃO PRINCIPAL DE GERAÇÃO DE CERTIFICADO ---

def gerar_certificado(nome_participante, cpf_usuario):
    """
    Gera um certificado de conclusão de curso para um participante específico.

    Args:
        nome_participante (str): O nome completo do participante.
        cpf_usuario (str): O CPF do participante.

    Returns:
        io.BytesIO: Um buffer de bytes contendo o arquivo PDF do certificado.
    """
    # --- 1. CONFIGURAÇÕES ---
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    tamanho_fonte_Nome = 150
    cor_fonte_RGB_Nome = (43, 121, 253)
    position_nome = (485, 700)
    nameFont_path = os.path.join(base_dir, "static/fonts/Handjet/static/Handjet-Medium.ttf")

    tamanho_fonte_Normal = 35
    cor_fonte_RGB_Normal = (71, 71, 71)
    position_texto_Normal = (485, 820)
    fonte_path_Normal = os.path.join(base_dir, "static/fonts/lucida-console/lucon.ttf")

    template_path = os.path.join(base_dir, "static/Images/CErtificado.png")
    
    # --- 2. VALIDAÇÃO ---
    if not nome_participante or not cpf_usuario:
        raise ValueError("O nome e o CPF do participante são obrigatórios.")

    # --- 3. PREPARAÇÃO DOS TEXTOS ---
    texto_nome = nome_participante.upper()
    
    # CORREÇÃO: Usando triple-quoted f-string para evitar o SyntaxError
    texto_normal_template = (
        f"Dono(a) do cpf: {cpf_usuario}"
        "Completou o curso online: “Combata o bullying com conhecimento. "
        "Torne-se um agente de mudança!” com carga horária de 20 minutos."
    )

    # --- 4. GERAÇÃO DA IMAGEM ---
    template = Image.open(template_path)
    desenho = ImageDraw.Draw(template)

    fonte_nome = ImageFont.truetype(nameFont_path, tamanho_fonte_Nome)
    fonte_normal = ImageFont.truetype(fonte_path_Normal, tamanho_fonte_Normal)

    desenho.text(position_nome, texto_nome, font=fonte_nome, fill=cor_fonte_RGB_Nome)
    
    linhas_texto_normal = textwrap.wrap(texto_normal_template, width=72)
    output_texto_normal = "\n".join(linhas_texto_normal)
    desenho.text(position_texto_Normal, output_texto_normal, font=fonte_normal, fill=cor_fonte_RGB_Normal)
    
    # --- 5. SALVAR EM MEMÓRIA ---
    if template.mode == 'RGBA':
        template = template.convert('RGB')
        
    buffer_pdf = io.BytesIO()
    template.save(buffer_pdf, format='PDF', resolution=100.0)
    buffer_pdf.seek(0)
    
    return buffer_pdf