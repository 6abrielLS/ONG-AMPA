import os
from django.core.exceptions import ValidationError


def validar_imagem(foto):
    # 1. Tamanho máximo (ex.: 5 MB)
    max_size = 5 * 1024 * 1024
    if foto.size > max_size:
        raise ValidationError("A imagem deve ter no máximo 5MB.")

    # 2. Extensões permitidas
    ext_permitidas = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(foto.name)[1].lower()

    if ext not in ext_permitidas:
        raise ValidationError("A imagem deve ser JPG ou PNG.")

    # 3. Sanitizar nome do arquivo
    foto.name = foto.name.replace(" ", "_")


def validar_pdf(arquivo):
    # 1. Valida a extensão
    ext = os.path.splitext(arquivo.name)[1].lower()
    
    if ext != '.pdf':
        raise ValidationError("Formato inválido. Envie apenas arquivos PDF.")

    # Tamanho máximo
    limit_mb = 3
    if arquivo.size > limit_mb * 1024 * 1024:
        raise ValidationError(f"O arquivo é muito grande. O limite é {limit_mb}MB.")
