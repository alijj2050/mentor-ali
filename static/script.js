// تغییر تم رنگی
document.getElementById('theme-dropdown').addEventListener('change', function () {
    const theme = this.value;
    document.body.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
});

// بارگذاری تم ذخیره‌شده کاربر
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    document.body.setAttribute('data-theme', savedTheme);
    document.getElementById('theme-dropdown').value = savedTheme;
}

// نمایش و مخفی کردن منوی کشویی
document.getElementById('menu-icon').addEventListener('click', function () {
    const dropdownMenu = document.getElementById('dropdown-menu');
    dropdownMenu.classList.toggle('active');
});

// بستن منوی کشویی هنگام کلیک خارج از آن
document.addEventListener('click', function (event) {
    const dropdownMenu = document.getElementById('dropdown-menu');
    const menuIcon = document.getElementById('menu-icon');
    if (!menuIcon.contains(event.target) && !dropdownMenu.contains(event.target)) {
        dropdownMenu.classList.remove('active');
    }
});

// اضافه کردن رفتار به موارد منو
document.getElementById('theme-color').addEventListener('click', function (event) {
    event.preventDefault();
    document.getElementById('theme-dropdown').click();
});

document.getElementById('clear-chat').addEventListener('click', function (event) {
    event.preventDefault();
    clearChat();
});

document.getElementById('report').addEventListener('click', function (event) {
    event.preventDefault();
    getChatReport();
});

// پاک کردن چت
function clearChat() {
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = '';
    alert('چت با موفقیت پاک شد.');
}

// دریافت گزارش چت
function getChatReport() {
    const phoneNumber = localStorage.getItem('phone-number');
    if (!phoneNumber) {
        alert('لطفاً ابتدا وارد شوید.');
        return;
    }

    fetch('/chat_report', {
        method: 'GET',
        headers: {
            'phone-number': phoneNumber,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.chat_report && data.chat_report.length > 0) {
            const report = data.chat_report.map(chat => `سوال: ${chat.question}\nپاسخ: ${chat.answer}`).join('\n\n');
            alert('گزارش چت:\n\n' + report);
        } else {
            alert('هیچ گزارشی وجود ندارد.');
        }
    })
    .catch(error => {
        console.error('Error fetching chat report:', error);
        alert('خطا در دریافت گزارش چت.');
    });
}

// ثبت نام کاربر
document.getElementById('register-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const phoneNumber = document.getElementById('phone-number').value;

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name: name, phone_number: phoneNumber }),
        });

        if (!response.ok) {
            throw new Error('خطا در ثبت نام');
        }

        const data = await response.json();
        alert(data.message);

        // نمایش فرم پرسش و پاسخ و مخفی کردن فرم ثبت‌نام
        document.getElementById('register-section').style.display = 'none';
        document.getElementById('ask-section').style.display = 'block';

        // نمایش بخش سوالات متداول
        document.getElementById('faq-section').style.display = 'block';

        // ذخیره شماره موبایل و وضعیت ثبت‌نام در localStorage
        localStorage.setItem('phone-number', phoneNumber);
        localStorage.setItem('isRegistered', 'true');
    } catch (error) {
        alert(error.message);
    }
});

// ارسال سوال و دریافت پاسخ
document.getElementById('ask-form').addEventListener('submit', async function (event) {
    event.preventDefault();

    // بررسی ثبت‌نام کاربر
    const isRegistered = localStorage.getItem('isRegistered');
    if (!isRegistered) {
        alert('لطفاً ابتدا ثبت‌نام کنید.');
        return;
    }

    const phoneNumber = localStorage.getItem('phone-number');
    if (!phoneNumber) {
        alert('لطفاً ابتدا وارد شوید.');
        return;
    }

    const question = document.getElementById('question').value;
    const responseDiv = document.getElementById('response');
    responseDiv.innerHTML = '<div class="loading">در حال پردازش...</div>';
    responseDiv.style.opacity = '1';

    try {
        const response = await fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'phone-number': phoneNumber,
            },
            body: JSON.stringify({ text: question }),
        });

        if (!response.ok) {
            throw new Error('خطا در ارسال درخواست');
        }

        const data = await response.json();
        responseDiv.innerHTML = `<p>${data.answer.replace(/\n/g, '<br>')}</p>`;

        // پاک کردن فیلد سوال پس از 5 ثانیه
        setTimeout(() => {
            const questionInput = document.getElementById('question');
            questionInput.value = '';
            questionInput.placeholder = 'سوال بعدی خود را اینجا بنویسید...';
            questionInput.classList.add('fade-out');
            setTimeout(() => questionInput.classList.remove('fade-out'), 500);
        }, 5000);
    } catch (error) {
        responseDiv.innerHTML = `<p class="error">${error.message}</p>`;
    }
});

// تشخیص گفتار
if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.lang = 'fa-IR';
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    const speechButton = document.getElementById('speech-button');
    const questionInput = document.getElementById('question');

    speechButton.addEventListener('click', () => {
        recognition.start();
        speechButton.textContent = 'در حال گوش دادن...';
    });

    recognition.addEventListener('result', (event) => {
        const transcript = event.results[0][0].transcript;
        questionInput.value = transcript;
        speechButton.textContent = '🎤';
    });

    recognition.addEventListener('end', () => {
        speechButton.textContent = '🎤';
    });

    recognition.addEventListener('error', (event) => {
        console.error('خطا در تشخیص گفتار:', event.error);
        speechButton.textContent = '🎤';
        alert('خطا در تشخیص گفتار. لطفاً دوباره امتحان کنید.');
    });
} else {
    console.warn('مرورگر شما از تشخیص گفتار پشتیبانی نمی‌کند.');
    document.getElementById('speech-button').style.display = 'none';
}

// تغییر انیمیشن‌ها به‌صورت چرخشی
const animations = document.querySelectorAll('.animation');
let currentAnimation = 0;

setInterval(() => {
    animations[currentAnimation].classList.remove('active');
    currentAnimation = (currentAnimation + 1) % animations.length;
    animations[currentAnimation].classList.add('active');
}, 5000);

// لیست سوالات متداول با ایموجی‌ها
const faqQuestions = [
    { question: "لیست غذا بده ؟", emoji: "🍔" },
    { question: "دسر دارید ؟", emoji: "🍰" },
    { question: " قیمت سفارشات؟", emoji: "💲" },
    { question: "آدرس شما کجاست؟", emoji: "📍" },
    { question: "ساعت کاری شما چیه؟", emoji: "⏰" },
    { question: "تخفیف ویژه دارید؟", emoji: "🎉" }
];

// تابع برای چرخش سوالات
function rotateFAQ() {
    const faqList = document.querySelector('.faq-list');
    let currentIndex = 0;

    setInterval(() => {
        faqList.innerHTML = ''; // پاک کردن سوالات قبلی

        // اضافه کردن 3 سوال جدید
        for (let i = 0; i < 3; i++) {
            const questionIndex = (currentIndex + i) % faqQuestions.length;
            const faq = faqQuestions[questionIndex];

            const button = document.createElement('button');
            button.className = 'suggested-question';
            button.setAttribute('data-question', faq.question);

            const emojiSpan = document.createElement('span');
            emojiSpan.textContent = faq.emoji;

            button.appendChild(emojiSpan);
            button.appendChild(document.createTextNode(faq.question));

            button.addEventListener('click', function () {
                const isRegistered = localStorage.getItem('isRegistered');
                if (!isRegistered) {
                    alert('لطفاً ابتدا ثبت‌نام کنید.');
                    return;
                }

                const phoneNumber = localStorage.getItem('phone-number');
                if (!phoneNumber) {
                    alert('لطفاً ابتدا وارد شوید.');
                    return;
                }

                const question = this.getAttribute('data-question');
                document.getElementById('question').value = question;
                document.getElementById('ask-form').dispatchEvent(new Event('submit'));
            });

            faqList.appendChild(button);
        }

        currentIndex = (currentIndex + 3) % faqQuestions.length;
    }, 5000); // تغییر سوالات هر 5 ثانیه
}

// اجرای تابع چرخش سوالات پس از بارگذاری صفحه
document.addEventListener('DOMContentLoaded', rotateFAQ);

// افزودن رفتار به سوالات پیشنهادی
document.querySelectorAll('.suggested-question').forEach(button => {
    button.addEventListener('click', function () {
        // بررسی ثبت‌نام کاربر
        const isRegistered = localStorage.getItem('isRegistered');
        if (!isRegistered) {
            alert('لطفاً ابتدا ثبت‌نام کنید.');
            return;
        }

        const phoneNumber = localStorage.getItem('phone-number');
        if (!phoneNumber) {
            alert('لطفاً ابتدا وارد شوید.');
            return;
        }

        const question = this.getAttribute('data-question');
        document.getElementById('question').value = question;

        // ارسال خودکار سوال به منتور
        document.getElementById('ask-form').dispatchEvent(new Event('submit'));
    });
});

// اضافه کردن عملکرد خروج
document.getElementById('logout').addEventListener('click', function (event) {
    event.preventDefault(); // جلوگیری از رفتار پیش‌فرض لینک

    // پاک کردن اطلاعات کاربر از localStorage
    localStorage.removeItem('phone-number');
    localStorage.removeItem('isRegistered');
    localStorage.removeItem('theme');

    // نمایش پیام خروج
    alert('شما با موفقیت از سیستم خارج شدید.');

    // هدایت کاربر به صفحه اصلی یا صفحه ورود
    window.location.href = '/'; // تغییر این آدرس به صفحه مورد نظر شما
});