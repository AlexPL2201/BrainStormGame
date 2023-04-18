function start_count() {
    $('.lobby_countdown_block').css('display', 'block');
    $('#min').html('0' + min);
    $('#sec').html('0' + sec);
    interval = window.setInterval(() => {
        if(sec == 59) {
            sec = 0;
            min++;
            if(min < 10) {
                $('#min').html('0' + min);
            } else {
                $('#min').html(min);
            }
        } else {
            sec++;
        }
        if(sec < 10) {
            $('#sec').html('0' + sec);
        } else {
            $('#sec').html(sec);
        }
    }, 1000);
}

// функция создания сокета очереди
function create_queue_socket(queue_id) {
    // запуск сокета
    queueSocket = new WebSocket (
        'ws://' + window.location.host + '/ws/queue/' + queue_id
    );

    // метод при открытии сокета (пусто)
    queueSocket.onopen = (e) => {
        console.log('open')
        console.log(e)
    }

    // метод при получении сообщения
    queueSocket.onmessage = (e) => {
        // получение объекта сообщения и действия из него
        const data = JSON.parse(e.data)['message'];
        let action = data['action'];

        // запрос на подтверждение - создание кнопки и установление таймайта на её исчезновение
        if(action == 'accept_request') {
            $('body').append('<div class="lobby_accept_request_bg"><div class="lobby_accept_request_button"><span>Подтвердить</span></div></div>');
            window.setTimeout(() => {
                $('.lobby_accept_request_bg').remove();
                accept_count = 0;
                themes = [];
                if(accepted == false) {
                    cancel_queue(true);
                } else {
                    accepted = false;
                }
            }, 10000);
        // подсчёт подтверждений, если это последний пользователь, присоединившийся к очереди
        } else if(action == 'accept_count' && is_last_player) {
            accept_count++;
            if(Object.keys(data).includes('theme')) {
                themes.push(data['theme']);
            }
            // если получено необходимое количество подтверждений, запуск действий на серверной части,
            // необходимых для запуска игры
            if(accept_count == max_players) {
                $.ajax({
                    method: "get",
                    url: "/games/create_game/",
                    data: {themes: JSON.stringify(themes)},
                    success: (data) => {
                        // отправка пользователям в очереди ссылки для перехода в игру
                        queueSocket.send(
                            JSON.stringify({'message': {'action': 'create_game', 'url': data.url}})
                        )
                    },
                    error: (data) => {
                    }
                });
            };
        // переход в игру по ссылке
        } else if(action == 'create_game') {
            window.location.href = data['url'];
        };
    };

    // метод при закрытии сокета (пусто)
    queueSocket.onclose = (e) => {
        console.log('close')
        console.log(e);
    }

    // метод при ошибке у сокета (пусто)
    queueSocket.onerror = (e) => {
        console.log('error')
        console.log(e)
    }
};

// функция проверки сокета и отправки запросов на подтверждение игры пользователям от последнего игрока в очереди
function connection_check() {
    // если сокет подключён и готов к работе, отправка запросов
    if(queueSocket.readyState === 1) {
        queueSocket.send(
            JSON.stringify({'message': {'action': 'accept_request'}})
        )
    // если нет, пробуем снова через 0.5 секунды
    } else {
        window.setTimeout(connection_check, 500);
    }
};

// функция выхода из очереди
function cancel_queue(is_canceler) {
    // необходимые изменения интерфейса
    $('.lobby_cancel_queue_button').html('Начать игру');
    $('.lobby_cancel_queue_button').addClass('lobby_start_game_button');
    $('.lobby_cancel_queue_button').removeClass('lobby_cancel_queue_button');

    // очистка отсчёта
    window.clearInterval(interval);
    sec = 0;
    min = 0;
    $('.lobby_countdown_block').css('display', '');
    $('#sec').html('');
    $('#min').html('');

    // закрытие сокета очереди и запуск соответствующих действий на серверной части
    queueSocket.close();
    if(is_canceler) {
        $.ajax({
        method: "get",
        url: "/games/cancel_queue/",
        data: {},
        success: (data) => {
        },
        error: (data) => {
        }
    });
    }
}

// функция выхода из лобби (запуск соответствующих действий на серверной части)
function quit_lobby() {
    $.ajax({
        method: "get",
        url: "/games/quit_lobby/",
        data: {},
        success: (data) => {
        },
        error: (data) => {
        }
    });
}
