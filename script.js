function switchTab(tabName) {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelector(`[onclick="switchTab('${tabName}')"]`).classList.add('active');
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`${tabName}-tab`).classList.add('active');
}

function previewImage(input) {
    const preview = document.getElementById('preview');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

function previewImageAsk(input) {
    const preview = document.getElementById('preview-ask');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            preview.src = e.target.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

async function analyzeImage() {
    const fileInput = document.getElementById('image-upload');
    const loadingDiv = document.getElementById('loading-analyze');
    const resultDiv = document.getElementById('result-analyze');

    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<div class="error"><i class="fas fa-exclamation-circle"></i> Please select an image first</div>';
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);

    loadingDiv.style.display = 'block';
    resultDiv.innerHTML = '';

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<div class="error"><i class="fas fa-exclamation-circle"></i> ${data.error}</div>`;
        } else {
            resultDiv.textContent = data.result;

            // Play audio if available
            if (data.audio_url) {
                playAudio(data.audio_url);
            }
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="error"><i class="fas fa-exclamation-circle"></i> Error: ${error.message}</div>`;
    } finally {
        loadingDiv.style.display = 'none';
    }
}

async function askQuestion() {
    const fileInput = document.getElementById('image-upload-ask');
    const questionInput = document.getElementById('question');
    const loadingDiv = document.getElementById('loading-ask');
    const resultDiv = document.getElementById('result-ask');

    if (!fileInput.files[0]) {
        resultDiv.innerHTML = '<div class="error"><i class="fas fa-exclamation-circle"></i> Please select an image first</div>';
        return;
    }

    if (!questionInput.value.trim()) {
        resultDiv.innerHTML = '<div class="error"><i class="fas fa-exclamation-circle"></i> Please enter a question</div>';
        return;
    }

    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    formData.append('question', questionInput.value);

    loadingDiv.style.display = 'block';
    resultDiv.innerHTML = '';

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();

        if (data.error) {
            resultDiv.innerHTML = `<div class="error"><i class="fas fa-exclamation-circle"></i> ${data.error}</div>`;
        } else {
            resultDiv.textContent = data.result;

            // Play audio if available
            if (data.audio_url) {
                playAudio(data.audio_url);
            }
        }
    } catch (error) {
        resultDiv.innerHTML = `<div class="error"><i class="fas fa-exclamation-circle"></i> Error: ${error.message}</div>`;
    } finally {
        loadingDiv.style.display = 'none';
    }
}

function playAudio(audioUrl) {
    const audio = new Audio(audioUrl);
    audio.play();
}
