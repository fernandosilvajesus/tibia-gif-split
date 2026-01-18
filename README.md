# Tibia GIF Split 🎬

Aplicação web para extrair frames de arquivos GIF e convertê-los para PNG com um nome customizado.

## Características

- ✅ Interface moderna e responsiva com Flask
- 📤 Upload de arquivos GIF com drag & drop
- 🎨 Nomeação customizada de frames (ex: walk_1, walk_2, ...)
- 🖼️ Preview dos frames em grid
- 📥 Download individual de frames
- 📦 Download de todos os frames em ZIP
- 📱 Design mobile-friendly
- 🔄 Processamento rápido com Pillow

## Requisitos

- Python 3.7+
- Flask
- Pillow (PIL)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/tibia_gif_split.git
cd tibia_gif_split
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Uso

1. Execute a aplicação:
```bash
python app.py
```

2. Abra seu navegador em:
```
http://localhost:5000
```

3. Siga os passos:
   - Selecione um arquivo GIF
   - Digite um nome para os frames (ex: "walk")
   - Clique em "Gerar Frames"
   - Baixe os frames individualmente ou em ZIP

## Estrutura do Projeto

```
tibia_gif_split/
├── app.py                 # Aplicação Flask principal
├── requirements.txt       # Dependências Python
├── .gitignore            # Arquivos ignorados no git
├── README.md             # Este arquivo
├── templates/
│   └── index.html        # Página principal (HTML)
├── static/
│   ├── style.css         # Estilos CSS
│   ├── script.js         # Lógica JavaScript
│   └── outputs/          # Pasta de saída dos frames
└── uploads/              # Pasta temporária de uploads
```

## API

### POST /upload
Faz upload e converte um GIF em frames PNG.

**Parâmetros:**
- `file` (file): Arquivo GIF
- `frame_name` (string, opcional): Nome customizado para os frames

**Resposta:**
```json
{
    "success": true,
    "total_frames": 8,
    "frames": [
        {
            "name": "walk_1.png",
            "path": "outputs/20260118_111345/walk_1.png",
            "index": 0
        }
    ],
    "output_dir": "static/outputs/20260118_111345"
}
```

### GET /download/<folder_name>
Faz download de todos os frames em um arquivo ZIP.

**Parâmetros:**
- `folder_name` (path): Nome da pasta com os frames

**Resposta:** Arquivo ZIP compactado

### GET /health
Verifica a saúde da aplicação.

## Configuração

No arquivo `app.py`, você pode ajustar:

```python
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # Tamanho máximo de upload (50MB)
app.config['UPLOAD_FOLDER'] = 'uploads'              # Pasta de uploads
app.config['OUTPUT_FOLDER'] = 'static/outputs'       # Pasta de saída
```

## Tecnologias Utilizadas

- **Backend:** Flask
- **Processamento de Imagens:** Pillow (PIL)
- **Frontend:** HTML5, CSS3, JavaScript Vanilla
- **Compressão:** Zipfile

## Licença

MIT License - sinta-se livre para usar este projeto!

## Autor

Criado com ❤️ para comunidade Tibia

---

**Dúvidas ou sugestões?** Abra uma issue no GitHub!
