const cartButton = document.querySelector("#cart-button");
const modal = document.querySelector(".modal");
const close = document.querySelector(".close");

cartButton.addEventListener("click", toggleModal);
close.addEventListener("click", toggleModal);

function toggleModal() {
  modal.classList.toggle("is-open");
}

new WOW().init();


document.addEventListener('DOMContentLoaded', function() {
    const recommendationsButton = document.getElementById('recommendations');
    const sushiButton = document.getElementById('sushi');
    const rollsButton = document.getElementById('rolls');
    const deliveryButton = document.getElementById('delivery'); // Кнопка "Доставка"
    const menuContent = document.getElementById('menu-content');
    const deliveryModal = document.getElementById('delivery-modal');
    const deliveryStatus = document.getElementById('delivery-status');
    const closeModalButton = document.querySelector('.close');

    // Данные о блюдах (замените на ваши реальные данные)
    const allDishes = [
        { id: 1, type: 'sushi', name: 'Лосось', description: 'Суши с лососем', price: 150 },
        { id: 2, type: 'sushi', name: 'Тунец', description: 'Суши с тунцом', price: 180 },
        { id: 3, type: 'rolls', name: 'Филадельфия', description: 'Ролл с лососем и сыром', price: 350 },
        { id: 4, type: 'rolls', name: 'Калифорния', description: 'Ролл с крабом и авокадо', price: 300 },
        { id: 5, type: 'sushi', name: 'Угорь', description: 'Суши с угрем', price: 200 },
        { id: 6, type: 'rolls', name: 'Дракон', description: 'Ролл с угрем и авокадо', price: 400 }
    ];

    // Функция для фильтрации блюд по типу
    function filterDishes(type) {
        return allDishes.filter(dish => dish.type === type);
    }

    // Функция для создания HTML для отображения блюд
    function createMenuHTML(dishes, title) {
        let html = <><h2>${title}</h2><ul>;
          dishes.forEach(dish ={">"} {html += <li>${dish.name} - ${dish.description} - ${dish.price}</li>};
          {"}"});
          html += </ul></>;
        return html;
    }

    // Функция для обновления контента меню
    function updateMenuContent(category) {
        let dishes;
        let title;

        if (category === 'recommendations') {
            dishes = allDishes;
            title = 'Рекомендации';
        } else if (category === 'sushi') {
            dishes = filterDishes('sushi');
            title = 'Суши';
        } else if (category === 'rolls') {
            dishes = filterDishes('rolls');
            title = 'Роллы';
        } else {
            menuContent.innerHTML = '<p>Неверная категория меню.</p>';
            return;
        }

        menuContent.innerHTML = createMenuHTML(dishes, title);
    }

    // Обработчики событий для кнопок меню
    recommendationsButton.addEventListener('click', function() {
        updateMenuContent('recommendations');
    });

    sushiButton.addEventListener('click', function() {
        updateMenuContent('sushi');
    });

    rollsButton.addEventListener('click', function() {
        updateMenuContent('rolls');
    });

    // Обработчик события для кнопки "Доставка"
    deliveryButton.addEventListener('click', function() {
        deliveryModal.style.display = "block"; // Показать модальное окно
        updateDeliveryStatus(); // Запустить обновление статуса
    });

    // Обработчик события для закрытия модального окна
    closeModalButton.addEventListener('click', function() {
        deliveryModal.style.display = "none"; // Скрыть модальное окно
    });

    // Функция для обновления статуса доставки
    function updateDeliveryStatus() {
        const statuses = ["Готовится...", "Едет к вам...", "Приехал!"];
        let currentStatusIndex = 0;

        function nextStatus() {
            deliveryStatus.textContent = statuses[currentStatusIndex];
            currentStatusIndex++;

            if (currentStatusIndex < statuses.length) {
                setTimeout(nextStatus, 20000); // Обновлять каждые 20 секунд
            } else {
                deliveryStatus.textContent = "Заказ доставлен!";
            }
        }

        nextStatus(); // Запустить первый статус
    }

    // Отображение рекомендаций по умолчанию при загрузке страницы
    updateMenuContent('recommendations');
});