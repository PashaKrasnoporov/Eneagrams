const sessionId = localStorage.getItem('enneagram_session');
if (!sessionId) window.location.href = '/payment';

let questions = [];
let currentIndex = 0;
let answers = [];
let selectedOption = null;

// Відновлення індекса питання
if (localStorage.getItem('enneagram_current_index')) {
    currentIndex = Number(localStorage.getItem('enneagram_current_index'));
}

// Відновлення відповідей, якщо вони вже були
if (localStorage.getItem('enneagram_answers')) {
    answers = JSON.parse(localStorage.getItem('enneagram_answers'));
}

const nextBtn = document.getElementById('nextBtn');
const prevBtn = document.getElementById('prevBtn');
const optionAButton = document.getElementById('optionA');
const optionBButton = document.getElementById('optionB');

async function loadQuestions() {
    try {
        const r = await fetch(`/api/test/questions?session_id=${sessionId}`);
        const d = await r.json();
        questions = d.questions || [];
        document.getElementById('totalQuestions').textContent = questions.length;
        showQuestion();
    } catch (e) {
        alert('❌ Помилка завантаження');
        window.location.href = '/payment';
    }
}

function showQuestion() {
    localStorage.setItem('enneagram_current_index', currentIndex);
    localStorage.setItem('enneagram_answers', JSON.stringify(answers));

    if (currentIndex >= questions.length) {
        submitTest();
        return;
    }

    const q = questions[currentIndex];
    const pct = Math.round(currentIndex / questions.length * 100);

    document.getElementById('currentQuestion').textContent = currentIndex + 1;
    document.getElementById('progressFill').style.width = pct + '%';
    document.getElementById('progressPercent').textContent = pct;

    document.getElementById('optionAText').textContent = q.option_a.text;
    document.getElementById('optionBText').textContent = q.option_b.text;

    prevBtn.style.display = currentIndex > 0 ? 'block' : 'none';

    // Скидаємо вибір
    selectedOption = null;
    optionAButton.classList.remove('active');
    optionBButton.classList.remove('active');

    // Блокуємо "Далі"
    nextBtn.disabled = true;
    nextBtn.classList.remove('btn-primary-active');
    nextBtn.textContent =
        currentIndex === questions.length - 1
            ? 'Завершити тест →'
            : 'Наступне питання →';
}

function select(opt) {
    selectedOption = opt;

    // підсвітка вибраної відповіді
    optionAButton.classList.toggle('active', opt === 'a');
    optionBButton.classList.toggle('active', opt === 'b');

    // розблокувати "Далі" і зробити яскравою
    nextBtn.disabled = false;
    nextBtn.classList.add('btn-primary-active');
}

function goNext() {
    if (!selectedOption) return; // без вибору не йдемо далі

    answers.push({
        question_id: questions[currentIndex].id,
        selected_option: selectedOption
    });

    currentIndex++;
    showQuestion();
}

function goBack() {
    if (currentIndex > 0) {
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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, answers })
        });
        const d = await r.json();
        localStorage.setItem('enneagram_result', JSON.stringify(d));
        localStorage.removeItem('enneagram_current_index');
        localStorage.removeItem('enneagram_answers');
        setTimeout(() => (window.location.href = '/result'), 1500);
    } catch (e) {
        alert('❌ Помилка');
    }
}

// Обробники для кнопок варіантів
optionAButton.addEventListener('click', () => select('a'));
optionBButton.addEventListener('click', () => select('b'));

// Обробники навігації
prevBtn.addEventListener('click', goBack);
nextBtn.addEventListener('click', () => {
    if (currentIndex < questions.length) {
        goNext();
    }
});

loadQuestions();
