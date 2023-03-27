window.addEventListener('load', () => {

    let userSocket, queueSocket;
    let interval;
    let sec = 0;
    let min = 0;
    let max_players, queue_id;
    let accept_count = 0;
    let is_last_player = false;
    let accepted = false;
    let user_id = $('#user_id').val();
    let sender;

    // запуск сокета
    userSocket = new WebSocket (
        'ws://' + window.location.host + '/ws/user/' + user_id
    );

    // метод при открытии сокета (пусто)
    userSocket.onopen = (e) => {
        console.log('open')
        console.log(e)
    }

    // метод при получении сообщения
    userSocket.onmessage = (e) => {
        // получение объекта сообщения и действия из него
        const data = JSON.parse(e.data)['message'];
        let action = data['action'];
        if(action == 'invitation') {
            sender = data['sender'];
            $('.lobby_invitation_nickname').html(`Принять приглашение от ${sender['nickname']}`);
            $('.lobby_invitation_accept').css('display', 'inline');
            $('.lobby_invitation_reject').css('display', 'inline');
        };
    };

    // метод при закрытии сокета (пусто)
    userSocket.onclose = (e) => {
        console.log('close')
        console.log(e);
    }

    // метод при ошибке у сокета (пусто)
    userSocket.onerror = (e) => {
        console.log('error')
        console.log(e)
    }

    // функция проверки сокета и отправки запросов на подтверждение игры пользователям от последнего игрока в очереди
    function connection_check(last_player_id) {
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
    function cancel_queue() {
        // необходимые изменения интерфейса
        $('.lobby_cancel_queue_button').html('Начать игру');
        $('.lobby_cancel_queue_button').addClass('lobby_start_game_button');
        $('.lobby_cancel_queue_button').removeClass('lobby_cancel_queue_button');

        // очистка отсчёта
        window.clearInterval(interval);
        sec = 0;
        min = 0;
        $('#sec').html('');
        $('#min').html('');

        // закрытие сокета очереди и запуск соответствующих действий на серверной части
        queueSocket.close();
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

    $(document).on('change', '.lobby_change_mode', (event) => {

    });

    $(document).on('click', '.lobby_invite_friend', (event) => {
        let friend_id = event.target.id.replace('friend_', '');
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
                JSON.stringify({'message': {'action': 'invitation', 'sender': {'pk': user_id, 'nickname': $('.lobby_users>p:first-child').html()}}})
            )
        }

        // метод при получении сообщения
        friendSocket.onmessage = (e) => {
            // получение объекта сообщения и действия из него
            const data = JSON.parse(e.data)['message'];
            let action = data['action'];
            if(action == 'accept') {
                event.target.remove();
                $('.lobby_users').append(`<p id='user_${friend_id}'>${friend_name}</p>`);
                friendSocket.close();
            } else if(action == 'reject') {
                $('.lobby_invitation_rejected').css('display', 'inline');
                window.setTimeout(() => {
                    $('.lobby_invitation_rejected').css('display', 'none');
                }, 2000)
                friendSocket.close();
            }
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

    $(document).on('click', '.lobby_invitation_accept', () => {
        $.ajax({
            method: "get",
            url: "/games/join_lobby/",
            data: {sender_id: sender['pk']},
            success: (data) => {
                $('html').html(data);
                userSocket.send(
                    JSON.stringify({'message': {'action': 'accept'}})
                );
            },
            error: (data) => {
            }
        });
    });

    $(document).on('click', '.lobby_invitation_reject', () => {
        sender = undefined;
        $('.lobby_invitation_nickname').html('');
        $('.lobby_invitation_accept').css('display', 'none');
        $('.lobby_invitation_reject').css('display', 'none');
        userSocket.send(
            JSON.stringify({'message': {'action': 'reject'}})
        );
    });

    // обработчик события нажатия на кнопку поиска игры
    $(document).on('click', '.lobby_start_game_button', (event) => {
        // необходимые изменения интерфейса
        event.target.innerHTML = 'Отменить поиск';
        event.target.classList.add('lobby_cancel_queue_button');
        event.target.classList.remove('lobby_start_game_button');

        // запуск отсчёта
        $('#min').html(min);
        $('#sec').html(sec);
        interval = window.setInterval(() => {
            if(sec == 59) {
                sec = 0;
                min++;
                $('#min').html(min);
            } else {
                sec++;
            }
            $('#sec').html(sec);
        }, 1000);

        // запуск соответствующих действий на серверной части
        $.ajax({
            method: "get",
            url: "/games/queue/",
            data: {},
            success: (data) => {
                // получение необходимых переменных с серверной части
                max_players = data.max_players;
                queue_id = data.queue_id;

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
                        $('body').append('<span class="lobby_accept_request_button">Подтвердить</span>');
                        window.setTimeout(() => {
                            $('.lobby_accept_request_button').remove();
                            accept_count = 0;
                            if(accepted == false) {
                                cancel_queue();
                            } else {
                                accepted = false;
                            }
                        }, 10000);
                    // подсчёт подтверждений, если это последний пользователь, присоединившийся к очереди
                    } else if(action == 'accept_count' && is_last_player) {
                        accept_count++;

                        // если получено необходимое количество подтверждений, запуск действий на серверной части,
                        // необходимых для запуска игры
                        if(accept_count == max_players) {
                            $.ajax({
                                method: "get",
                                url: "/games/create_game/",
                                data: {},
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

        // отправка другим пользователям в очереди сообщения о том, что запрос подтверждён
        queueSocket.send(
            JSON.stringify({'message': {'action': 'accept_count'}})
        );
    });

    // обработчик события нажатия на кнопку отмены поиска игры
    $(document).on('click', '.lobby_cancel_queue_button', () => {
        cancel_queue();
    });

    // обработчик события закрытия окна, перехода на другую страницу или обновления страницы
    window.addEventListener('beforeunload', () => {
        quit_lobby();
    });

});