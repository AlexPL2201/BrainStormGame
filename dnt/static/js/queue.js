window.addEventListener('load', () => {

    $(document).on('change', '.lobby_change_mode', (event) => {
        let mode = event.target.value;
        $.ajax({
            method: "get",
            url: "/games/change_game_mode/",
            data: {mode: mode},
            success: (data) => {
                console.log(data)
            },
            error: (data) => {
            }
        });
    });

    $(document).on('click', '.header_friend_invite', (event) => {
        let friend_id = event.target.id.replace('invite_friend_', '');
        let friend_name = event.target.innerHTML;

        // запуск сокета
        friendSocket = new WebSocket (
            'ws://' + window.location.host + '/ws/user/' + friend_id
        );

        // метод при открытии сокета (пусто)
        friendSocket.onopen = (e) => {
            console.log('open')
            console.log(e)
            friendSocket.send(
                JSON.stringify({'message': {'action': 'invitation', 'sender': {'pk': user_id, 'nickname': $('.lobby_the_player>span:first-child').html()}}})
            )
        }

        // метод при получении сообщения
        friendSocket.onmessage = (e) => {
            // получение объекта сообщения и действия из него
            const data = JSON.parse(e.data)['message'];
            let action = data['action'];
            if(action == 'reject') {
                $('.lobby_invitation_rejected').css('display', 'inline');
                window.setTimeout(() => {
                    $('.lobby_invitation_rejected').css('display', 'none');
                }, 2000)
                friendSocket.close();
            } else if(action == 'accept') {
                friendSocket.close();
            };
        };

        // метод при закрытии сокета (пусто)
        friendSocket.onclose = (e) => {
            console.log('close')
            console.log(e);
        }

        // метод при ошибке у сокета (пусто)
        friendSocket.onerror = (e) => {
            console.log('error')
            console.log(e)
        }
    });

    // обработчик события нажатия на кнопку поиска игры
    $(document).on('click', '.lobby_start_game_button', (event) => {
        // необходимые изменения интерфейса
        event.target.innerHTML = 'Отменить поиск';
        event.target.classList.add('lobby_cancel_queue_button');
        event.target.classList.remove('lobby_start_game_button');

        // запуск отсчёта
        start_count();

        // запуск соответствующих действий на серверной части
        $.ajax({
            method: "get",
            url: "/games/queue/",
            data: {},
            success: (data) => {
                // получение необходимых переменных с серверной части
                queue_id = data.queue_id;

                // создание сокета очереди
                create_queue_socket(queue_id);

                // если пользователь - последний в очереди, запуска процесса подтверждений
                if(data.result == 'start') {
                    is_last_player = true;
                    connection_check();
                }
            },
            error: (data) => {
            }
        });
    });

    // обработчик события нажатия на кнопку для подтверждения игры
    $(document).on('click', '.lobby_accept_request_button', () => {
        accepted = true;
        data = {'action': 'accept_count'};
        if($('.lobby_theme').length) {
            data['theme'] = $('.lobby_theme').val();
        }
        // отправка другим пользователям в очереди сообщения о том, что запрос подтверждён
        queueSocket.send(
            JSON.stringify({'message': data})
        );
    });

    // обработчик события нажатия на кнопку отмены поиска игры
    $(document).on('click', '.lobby_cancel_queue_button', () => {
        cancel_queue(true);
    });

    // обработчик события закрытия окна, перехода на другую страницу или обновления страницы
    window.addEventListener('beforeunload', () => {
        quit_lobby();
    });

});