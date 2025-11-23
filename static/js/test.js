const sessionId = localStorage.getItem('enneagram_session');
if(!sessionId) window.location.href = '/payment';

let questions = [],
    currentIndex = 0,
    answers = [];

// Відновлення індекса питання
if (localStorage.getItem('enneagram_current_index')) {
    currentIndex = Number(localStorage.getItem('enneagram_current_index'));
} else {
    currentIndex = 0;
}

// Відновлення відповідей, якщо вони вже були
if (localStorage.getItem('enneagram_answers')) {
    answers = JSON.parse(localStorage.getItem('enneagram_answers'));
} else {
    answers = [];
}

async function loadQuestions() {
    try {
        const r = await fetch(`/api/test/questions?session_id=${sessionId}`);
        const d = await r.json();
        questions = d.questions || [];
        document.getElementById('totalQuestions').textContent = questions.length;
        showQuestion();
    } catch(e) {
        alert('❌ Помилка завантаження');
        window.location.href = '/payment';
    }
}

function showQuestion() {
    localStorage.setItem('enneagram_current_index', currentIndex);
    localStorage.setItem('enneagram_answers', JSON.stringify(answers)); // збереження відповідей

    if(currentIndex >= questions.length) {
        submitTest();
    } else {
        const q = questions[currentIndex];
        const pct = Math.round(currentIndex / questions.length * 100);
        document.getElementById('currentQuestion').textContent = currentIndex + 1;
        document.getElementById('progressFill').style.width = pct + '%';
        document.getElementById('progressPercent').textContent = pct;
        document.getElementById('optionAText').textContent = q.option_a.text;
        document.getElementById('optionBText').textContent = q.option_b.text;
        document.getElementById('prevBtn').style.display = currentIndex > 0 ? 'block' : 'none';
    }
}

function select(opt) {
    answers.push({question_id: questions[currentIndex].id, selected_option: opt});
    currentIndex++;
    showQuestion();
}

function goBack() {
    if(currentIndex > 0) {
        currentIndex--;
        answers.pop();
        showQuestion();
    }
}

async function submitTest() {
    document.querySelector('.test-container').innerHTML =
        '<div style="text-align:center;padding:3rem"><h2 style="color:#0066CC">✨ Обробка результатів...</h2></div>';
    try {
        const r = await fetch('/api/test/submit', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({session_id: sessionId, answers})
        });
        const d = await r.json();
        localStorage.setItem('enneagram_result', JSON.stringify(d));
        // Після завершення тесту очищаємо прогрес і відповіді
        localStorage.removeItem('enneagram_current_index');
        localStorage.removeItem('enneagram_answers');
        setTimeout(() => window.location.href = '/result', 1500);
    } catch(e) {
        alert('❌ Помилка');
    }
}

// Обробники для кнопок
document.getElementById('optionA').addEventListener('click', () => select('a'));
document.getElementById('optionB').addEventListener('click', () => select('b'));
document.getElementById('prevBtn').addEventListener('click', goBack);

loadQuestions();
