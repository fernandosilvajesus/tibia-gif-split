"""
Conversor de GIF para PNG - Flask App
Aplicação web para extrair frames de GIFs e convertê-los em PNG.
"""

from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
import os
from pathlib import Path
import logging
from werkzeug.utils import secure_filename
import shutil
from datetime import datetime
import zipfile
from io import BytesIO

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB máximo
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'static/outputs'

ALLOWED_EXTENSIONS = {'gif'}

# Criar pastas se não existirem
Path(app.config['UPLOAD_FOLDER']).mkdir(exist_ok=True)
Path(app.config['OUTPUT_FOLDER']).mkdir(exist_ok=True)


def allowed_file(filename):
    """Verificar se o arquivo é GIF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class ConversorGIF:
    """Classe para converter frames de GIF para PNG."""

    def __init__(self, output_format: str = "PNG"):
        """
        Inicializar o conversor.
        
        Args:
            output_format: Formato de saída (padrão: PNG)
        """
        self.output_format = output_format

    def converter(self, gif_path: str, output_dir: str, frame_name_prefix: str = None) -> dict:
        """
        Converte todos os frames de um GIF em arquivos PNG.
        
        Args:
            gif_path: Caminho do arquivo GIF
            output_dir: Diretório de saída para os PNGs
            frame_name_prefix: Prefixo customizado para nomeação dos frames
            
        Returns:
            Dicionário com resultado da conversão
        """
        # Validar arquivo de entrada
        if not os.path.exists(gif_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {gif_path}")

        # Criar pasta de saída
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        logger.info(f"Pasta de saída: {output_dir}")

        frame_count = 0
        frames_info = []

        try:
            with Image.open(gif_path) as gif:
                logger.info(f"Processando: {gif_path}")
                
                frame_index = 0

                while True:
                    try:
                        # Converter frame para RGBA
                        frame = gif.convert("RGBA")

                        # Nome do arquivo
                        if frame_name_prefix:
                            frame_name = f"{frame_name_prefix}_{frame_index + 1}.{self.output_format.lower()}"
                        else:
                            frame_name = f"frame_{frame_index:04d}.{self.output_format.lower()}"
                        frame_path = os.path.join(output_dir, frame_name)

                        # Salvar frame
                        frame.save(frame_path, format=self.output_format)
                        
                        # Informações do frame para exibição
                        frames_info.append({
                            'name': frame_name,
                            'path': f"outputs/{os.path.basename(output_dir)}/{frame_name}",
                            'index': frame_index
                        })
                        
                        frame_count += 1
                        logger.debug(f"Frame {frame_index} salvo: {frame_path}")

                        # Próximo frame
                        gif.seek(frame_index + 1)
                        frame_index += 1

                    except EOFError:
                        break

        except Exception as e:
            logger.error(f"Erro ao processar GIF: {e}")
            raise

        logger.info(f"{frame_count} frames extraídos com sucesso!")
        
        return {
            'success': True,
            'total_frames': frame_count,
            'frames': frames_info,
            'output_dir': output_dir
        }


@app.route('/')
def index():
    """Página inicial."""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    """Processar upload e conversão de GIF."""
    try:
        # Verificar se arquivo foi enviado
        if 'file' not in request.files:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'Arquivo não selecionado'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Apenas arquivos GIF são permitidos'}), 400
        
        # Salvar arquivo temporário
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{timestamp}_{filename}")
        file.save(upload_path)
        
        # Criar pasta para saída
        output_folder_name = timestamp
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_folder_name)
        
        # Converter GIF
        conversor = ConversorGIF()
        
        # Obter nome customizado (opcional)
        frame_name_prefix = request.form.get('frame_name', '').strip()
        
        resultado = conversor.converter(upload_path, output_path, frame_name_prefix)
        
        # Limpar arquivo temporário
        os.remove(upload_path)
        
        return jsonify(resultado), 200
    
    except Exception as e:
        logger.error(f"Erro no upload: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Verificar saúde da aplicação."""
    return jsonify({'status': 'ok'}), 200


@app.route('/download/<folder_name>', methods=['GET'])
def download_all(folder_name):
    """Fazer download de todos os frames em um ZIP."""
    try:
        # Validar nome da pasta
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], folder_name)
        
        if not os.path.exists(output_path):
            return jsonify({'error': 'Pasta não encontrada'}), 404
        
        # Criar arquivo ZIP em memória
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Adicionar todos os frames ao ZIP
            for filename in sorted(os.listdir(output_path)):
                file_path = os.path.join(output_path, filename)
                if os.path.isfile(file_path):
                    # Adicionar ao ZIP com o caminho relativo
                    arcname = filename
                    zip_file.write(file_path, arcname=arcname)
        
        # Preparar para envio
        zip_buffer.seek(0)
        
        logger.info(f"Download ZIP: {folder_name}")
        
        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f'frames_{folder_name}.zip'
        )
    
    except Exception as e:
        logger.error(f"Erro ao fazer download: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
