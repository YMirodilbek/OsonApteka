const select = document.getElementById("lang-select");
const defaultLang = localStorage.getItem("lang") || "ru";
let langData = {}; // <--- bu yerda e'lon qilinadi

function loadLanguage(lang) {
    fetch(`/static/lang/${lang}.json`)
        .then(res => res.json())
        .then(data => {
            langData = data; // <--- JSON ma’lumotlari langData ga yuklanadi

            // HTML elementlarni tarjima qilish
            document.querySelectorAll("[data-i18n]").forEach(el => {
                const key = el.getAttribute("data-i18n");
                if(data[key]) el.innerText = data[key];
            });

            document.querySelectorAll("[data-i18n-placeholder]").forEach(el => {
                const key = el.getAttribute("data-i18n-placeholder");
                if(data[key]) el.placeholder = data[key];
            });

            // Agar mini cart ochiq bo‘lsa, uni ham yangilash
            if (typeof renderMiniCart === "function") renderMiniCart();
        });
}

// Boshlang‘ich tilni yuklash
loadLanguage(defaultLang);
select.value = defaultLang;

// Tilni o‘zgartirganda
select.addEventListener("change", e => {
    const lang = e.target.value;
    localStorage.setItem("lang", lang);
    loadLanguage(lang);
});