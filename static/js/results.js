const result = localStorage.getItem('enneagram_result');
if (!result) {
    alert('Ви ще не пройшли тест. Результати доступні лише після проходження!');
    window.location.href = '/test';
}

// Далі твій код для отримання та показу результату
