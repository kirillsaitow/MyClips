// Навигация по секциям
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        document.querySelectorAll('section').forEach(section => {
            section.classList.add('hidden-section');
            if (section.id === `${btn.dataset.section}-section`) {
                section.classList.remove('hidden-section');
            }
        });
    });
});

// Избранное
async function toggleFavorite(filename, event) {
    event.stopPropagation();
    const btn = event.target.closest('.favorite-btn');

    try {
        const response = await fetch('/favorite', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({filename: filename})
        });

        const data = await response.json();

        if(data.status === 'success') {
            btn.classList.toggle('active', data.action === 'added');
            btn.textContent = data.action === 'added' ? '★' : '☆';

            // Обновляем счетчик избранного
            const favoritesCount = document.querySelector('.favorites-count');
            if(favoritesCount) {
                favoritesCount.textContent = data.favorites.length;
            }
        }
    } catch(error) {
        console.error('Ошибка:', error);
    }
}

// Инициализация состояния кнопок при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    const favorites = document.cookie
        .split('; ')
        .find(row => row.startsWith('favorites='))
        ?.split('=')[1]
        ?.split(',') || [];

    favorites.forEach(filename => {
        const btn = document.querySelector(`.clip-card[data-filename="${filename}"] .favorite-btn`);
        if(btn) {
            btn.classList.add('active');
            btn.textContent = '★';
        }
    });
});

// function changeViewMode(mode) {
//     const container = document.querySelector('.clips-container');
//     container.className = `clips-container clips-${mode}`;
//
//     document.cookie = `view_mode=${mode}; path=/; max-age=2592000`;
//
//     // Обновление активных кнопок
//     document.querySelectorAll('.view-btn').forEach(btn => {
//         btn.classList.toggle('active', btn.dataset.mode === mode);
//     });
// }

// Поиск
function searchClips() {
    const query = document.getElementById('search').value;
    window.location.href = `/?q=${encodeURIComponent(query)}`;
}

// Редактор видео
const videoUpload = document.getElementById('video-upload');
const editorVideo = document.getElementById('editor-video');
const startSlider = document.getElementById('start-slider');
const endSlider = document.getElementById('end-slider');

videoUpload.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const url = URL.createObjectURL(file);
        editorVideo.src = url;
    }
});



// Открытие видео
function openVideo(filename) {
    const modal = document.getElementById('video-modal');
    const player = document.getElementById('video-player');

    player.src = `/video/${filename}`;
    player.load();

    player.onloadeddata = () => {
        modal.style.display = 'block';
        player.play().catch(error => {
            player.controls = true;
        });
    };

    player.onerror = () => {
        alert('Ошибка загрузки видео');
        modal.style.display = 'none';
    };
}

// Удаление клипа
function confirmDelete(filename) {
    if(confirm(`Удалить клип "${filename}"?`)) {
        fetch(`/delete/${filename}`, { method: 'POST' })
            .then(response => {
                if(response.ok) window.location.reload();
                else alert('Ошибка удаления');
            });
    }
}

// Переименование клипа
function showRenameForm(filename) {
    const newName = prompt('Введите новое имя:', filename.replace('.mp4', ''));
    if(newName && newName !== filename) {
        const formData = new FormData();
        formData.append('new_name', newName);

        fetch(`/rename/${filename}`, {
            method: 'POST',
            body: formData
        })
            .then(response => {
                if(response.ok) window.location.reload();
                else alert('Ошибка переименования');
            });
    }
}

// Закрытие видео
function closeVideo() {
    const modal = document.getElementById('video-modal');
    const player = document.getElementById('video-player');

    player.pause();
    player.currentTime = 0;
    modal.style.display = 'none';
}

// Обработчик клика вне модального окна
window.onclick = function(event) {
    const modal = document.getElementById('video-modal');
    if(event.target === modal) {
        closeVideo();
    }
}


// Мобильное меню
function toggleMenu() {
    document.querySelector('.sidebar').classList.toggle('active');
}

// Закрытие меню при клике вне его области
document.addEventListener('click', (e) => {
    const sidebar = document.querySelector('.sidebar');
    const menuToggle = document.querySelector('.menu-toggle');

    if (window.innerWidth <= 768 && !sidebar.contains(e.target) && !menuToggle.contains(e.target)) {
        sidebar.classList.remove('active');
    }
});

document.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', (e) => {
        if (link.href.includes(window.location.origin)) {
            document.body.classList.add('page-loading');
        }
    });
});

// Сворачивание меню
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

// Обработчики закрытия видео
document.addEventListener('keydown', (e) => {
    if(e.key === 'Escape') closeVideo();
});

document.getElementById('video-modal').addEventListener('click', (e) => {
    if(e.target === document.getElementById('video-modal')) closeVideo();
});