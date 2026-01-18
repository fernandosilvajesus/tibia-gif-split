// Elementos do DOM
const uploadBox = document.getElementById('uploadBox');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// Drag and Drop
uploadBox.addEventListener('dragover', handleDragOver);
uploadBox.addEventListener('dragleave', handleDragLeave);
uploadBox.addEventListener('drop', handleDrop);

fileInput.addEventListener('change', handleFileSelect);

// Handlers
function handleDragOver(e) {
    e.preventDefault();
    uploadBox.style.borderColor = '#ec4899';
    uploadBox.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(236, 72, 153, 0.15) 100%)';
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadBox.style.borderColor = '#6366f1';
    uploadBox.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%)';
}

function handleDrop(e) {
    e.preventDefault();
    uploadBox.style.borderColor = '#6366f1';
    uploadBox.style.background = 'linear-gradient(135deg, rgba(99, 102, 241, 0.05) 0%, rgba(236, 72, 153, 0.05) 100%)';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        fileInput.files = files;
        handleFileSelect();
    }
}

function handleFileSelect() {
    const file = fileInput.files[0];
    
    if (!file) return;

    // Validar tipo de arquivo
    if (!file.name.toLowerCase().endsWith('.gif')) {
        showError('Por favor, selecione um arquivo GIF válido');
        return;
    }

    // Exibir informações do arquivo
    document.getElementById('fileName').textContent = `Arquivo: ${file.name}`;
    document.getElementById('fileSize').textContent = `Tamanho: ${(file.size / 1024 / 1024).toFixed(2)} MB`;
    fileInfo.classList.remove('hidden');

    // Limpar input de nome anterior
    document.getElementById('customName').value = '';

    // Scroll para input de nome
    document.getElementById('customName').focus();
}

async function uploadFile(file) {
    const formData = new FormData();
    
    // Se não passou o arquivo, use o que foi selecionado
    if (!file) {
        file = fileInput.files[0];
        if (!file) {
            showError('Nenhum arquivo selecionado');
            return;
        }
    }
    
    formData.append('file', file);
    
    // Obter nome customizado
    const customName = document.getElementById('customName').value.trim();
    if (customName) {
        formData.append('frame_name', customName);
    }

    try {
        // Mostrar seção de progresso
        progressSection.classList.remove('hidden');
        errorSection.classList.add('hidden');
        resultsSection.classList.add('hidden');

        // Enviar arquivo
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Erro ao processar arquivo');
        }

        // Sucesso!
        displayResults(data);

    } catch (error) {
        showError(error.message);
    }
}

function displayResults(data) {
    // Ocultar progresso
    progressSection.classList.add('hidden');

    // Atualizar contagem de frames
    document.getElementById('frameCount').textContent = `${data.total_frames} frames extraídos com sucesso`;

    // Limpar grid anterior
    const framesGrid = document.getElementById('framesGrid');
    framesGrid.innerHTML = '';

    // Adicionar frames
    data.frames.forEach((frame) => {
        const frameElement = createFrameElement(frame);
        framesGrid.appendChild(frameElement);
    });

    // Mostrar resultados
    resultsSection.classList.remove('hidden');

    // Scroll para resultados
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    // Guardar folder_name para download completo
    window.currentFolderName = data.output_dir.split('\\').pop() || data.output_dir.split('/').pop();
}

function createFrameElement(frame) {
    const div = document.createElement('div');
    div.className = 'frame-item';

    const img = document.createElement('img');
    img.src = `/static/${frame.path}`;
    img.alt = frame.name;
    img.className = 'frame-image';
    img.onerror = () => {
        img.src = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="150" height="140"%3E%3Crect fill="%23e2e8f0" width="150" height="140"/%3E%3Ctext x="50%25" y="50%25" dominant-baseline="middle" text-anchor="middle" font-family="Arial" font-size="12" fill="%2364748b"%3EErro ao carregar%3C/text%3E%3C/svg%3E';
    };

    const name = document.createElement('div');
    name.className = 'frame-name';
    name.textContent = frame.name;

    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'frame-download';
    downloadBtn.innerHTML = '⬇️';
    downloadBtn.title = 'Download';
    downloadBtn.onclick = (e) => {
        e.stopPropagation();
        downloadFrame(frame);
    };

    div.appendChild(img);
    div.appendChild(name);
    div.appendChild(downloadBtn);

    return div;
}

function downloadFrame(frame) {
    const link = document.createElement('a');
    link.href = `/static/${frame.path}`;
    link.download = frame.name;
    link.click();
}

function downloadAllFrames() {
    if (!window.currentFolderName) {
        alert('Erro: pasta não encontrada');
        return;
    }
    
    const link = document.createElement('a');
    link.href = `/download/${window.currentFolderName}`;
    link.download = `frames_${window.currentFolderName}.zip`;
    link.click();
}

function showError(message) {
    progressSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    
    document.getElementById('errorMessage').textContent = `❌ ${message}`;
    errorSection.classList.remove('hidden');

    // Scroll para erro
    errorSection.scrollIntoView({ behavior: 'smooth' });
}

function resetForm() {
    // Resetar inputs
    fileInput.value = '';
    fileInfo.classList.add('hidden');

    // Ocultar seções
    progressSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');

    // Scroll para upload
    uploadBox.scrollIntoView({ behavior: 'smooth' });
}

// Permitir clique no upload box para abrir seletor
uploadBox.addEventListener('click', () => {
    fileInput.click();
});
