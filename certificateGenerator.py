from PIL import Image, ImageDraw, ImageFont
import textwrap
import io

# --- FUNÇÕES AUXILIARES (sem alterações) ---

def gerarNomeArquivo(nome_completo):
    """Gera um nome de arquivo simplificado a partir de um nome completo."""
    partes = nome_completo.split(" ")
    if not partes:
        return "certificado.pdf"
    
    iniciais = "".join([p[0] for p in partes if p]).upper()
    nome_arquivo = f"{partes[0].lower()}_{iniciais}.pdf"
    return nome_arquivo

# --- FUNÇÃO PRINCIPAL DE GERAÇÃO DE CERTIFICADO (ATUALIZADA) ---

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
    # Rotina para o texto do Nome
    tamanho_fonte_Nome = 50
    cor_fonte_RGB_Nome = (43, 121, 253)
    position_nome = (305, 150)
    nameFont_path = "/static/fonts/Handjet/Handjet-Medium.ttf"

    # Rotina para o texto Normal
    tamanho_fonte_Normal = 20
    cor_fonte_RGB_Normal = (71, 71, 71)
    position_texto_Normal = (305, 245)
    fonte_path_Normal = "/static/fonts/lucida-console/lucon.ttf"

    # Geral
    template_path = "static/images/CErtificado.png"
    
    # --- 2. VALIDAÇÃO DOS DADOS DE ENTRADA ---
    if not nome_participante or not cpf_usuario:
        raise ValueError("O nome e o CPF do participante são obrigatórios.")

    # --- 3. PREPARAÇÃO DOS TEXTOS ---
    
    # Texto para a rotina do NOME
    texto_nome = nome_participante.upper()

    # Texto para a rotina NORMAL (com o novo template)
    # Adicionei "\n\n" para separar as linhas e melhorar a legibilidade.
    texto_normal_template = (
        f"Dono(a) do cpf: {cpf_usuario}\n\n"
        "Completou o curso online: “Combata o bullying com conhecimento. "
        "Torne-se um agente de mudança!” com carga horária de 20 minutos."
    )

    # --- 4. GERAÇÃO DA IMAGEM E ESCRITA ---
    template = Image.open(template_path)
    desenho = ImageDraw.Draw(template)

    # Carregar fontes para cada rotina
    fonte_nome = ImageFont.truetype(nameFont_path, tamanho_fonte_Nome)
    fonte_normal = ImageFont.truetype(fonte_path_Normal, tamanho_fonte_Normal)

    # **Rotina 1: Escrever o nome do participante**
    desenho.text(position_nome, texto_nome, font=fonte_nome, fill=cor_fonte_RGB_Nome)

    # **Rotina 2: Escrever o texto normal**
    # Quebra de linha para o texto normal se ele for muito longo
    linhas_texto_normal = textwrap.wrap(texto_normal_template, width=72)
    output_texto_normal = '\n'.join(linhas_texto_normal)
    desenho.text(position_texto_Normal, output_texto_normal, font=fonte_normal, fill=cor_fonte_RGB_Normal)
    
    # --- 5. SALVAR EM MEMÓRIA ---
    if template.mode == 'RGBA':
        template = template.convert('RGB')
        
    buffer_pdf = io.BytesIO()
    template.save(buffer_pdf, format='PDF', resolution=100.0)
    buffer_pdf.seek(0)
    
    return buffer_pdf