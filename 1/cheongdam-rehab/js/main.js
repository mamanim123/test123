// 모바일 메뉴 토글
const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
const mainNav = document.querySelector('.main-nav');
const navLinks = document.querySelectorAll('.main-nav a');

mobileMenuBtn.addEventListener('click', () => {
    mainNav.classList.toggle('active');
    mobileMenuBtn.querySelector('i').classList.toggle('fa-times');
    document.body.classList.toggle('no-scroll');
});

// 네비게이션 링크 클릭 시 모바일 메뉴 닫기
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        mainNav.classList.remove('active');
        mobileMenuBtn.querySelector('i').classList.remove('fa-times');
        document.body.classList.remove('no-scroll');
    });
});

// 스크롤 시 헤더 스타일 변경
const header = document.querySelector('.header');
let lastScroll = 0;

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;
    
    if (currentScroll <= 0) {
        header.classList.remove('scroll-up');
        return;
    }
    
    if (currentScroll > lastScroll && !header.classList.contains('scroll-down')) {
        // 스크롤 다운
        header.classList.remove('scroll-up');
        header.classList.add('scroll-down');
    } else if (currentScroll < lastScroll && header.classList.contains('scroll-down')) {
        // 스크롤 업
        header.classList.remove('scroll-down');
        header.classList.add('scroll-up');
    }
    
    lastScroll = currentScroll;
});

// 스무스 스크롤
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
            window.scrollTo({
                top: targetElement.offsetTop - 80,
                behavior: 'smooth'
            });
        }
    });
});

// 카운터 애니메이션
const counters = document.querySelectorAll('.counter');
let isAnimated = false;

function animateCounters() {
    if (isAnimated) return;
    
    const counterSection = document.querySelector('.infographic-section');
    const counterPosition = counterSection.getBoundingClientRect().top;
    const screenPosition = window.innerHeight / 1.3;
    
    if (counterPosition < screenPosition) {
        isAnimated = true;
        
        counters.forEach(counter => {
            const target = +counter.getAttribute('data-target');
            const count = +counter.innerText;
            const increment = target / 100;
            
            if (count < target) {
                counter.innerText = Math.ceil(count + increment);
                setTimeout(animateCounters, 30);
            } else {
                counter.innerText = target;
            }
        });
    }
}

// 스크롤 이벤트로 카운터 애니메이션 트리거
window.addEventListener('scroll', animateCounters);

// 폼 제출 처리
const contactForm = document.querySelector('.contact-form form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // 간단한 폼 유효성 검사
        const name = this.querySelector('input[type="text"]').value.trim();
        const phone = this.querySelector('input[type="tel"]').value.trim();
        const email = this.querySelector('input[type="email"]').value.trim();
        const message = this.querySelector('textarea').value.trim();
        const privacyAgree = this.querySelector('input[type="checkbox"]').checked;
        
        if (!name || !phone || !message || !privacyAgree) {
            alert('모든 필수 항목을 작성해주세요.');
            return;
        }
        
        // 여기서는 콘솔에만 출력하고 실제로는 서버로 전송해야 함
        console.log('폼 제출:', { name, phone, email, message });
        
        // 폼 제출 후 처리
        alert('문의가 접수되었습니다. 빠른 시일 내에 연락드리겠습니다.');
        this.reset();
    });
}

// 로딩 애니메이션
window.addEventListener('load', () => {
    document.body.classList.add('loaded');
});

// 애니메이션 트리거 (스크롤 시 요소 나타나기)
const animateOnScroll = () => {
    const elements = document.querySelectorAll('.info-card, .program-card, .facility-item, .contact-form');
    
    elements.forEach(element => {
        const elementTop = element.getBoundingClientRect().top;
        const windowHeight = window.innerHeight;
        
        if (elementTop < windowHeight - 100) {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }
    });
};

// 초기 애니메이션 상태 설정
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.info-card, .program-card, .facility-item, .contact-form');
    
    animatedElements.forEach(element => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(30px)';
        element.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    });
    
    // 초기 로드 시 한 번 실행
    animateOnScroll();
    
    // 스크롤 이벤트에 연결
    window.addEventListener('scroll', animateOnScroll);
});
