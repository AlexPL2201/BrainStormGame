window.addEventListener('load', () => {

    let notificationSocket;
    let interval;
    let sec = 0;
    let min = 0;
    let max_players, queue_id;
    let accept_count = 0;
    let is_last_player = false;
    let accepted = false;

    function connection_check(last_player_id) {
        if(notificationSocket.readyState === 1) {
            notificationSocket.send(
                JSON.stringify({'message': {'action': 'accept_request'}})
            )
        } else {
            window.setTimeout(connection_check, 500);
        }
    };

    function cancel_queue() {
        $('.lobby_cancel_queue_button').html('Start game');
        $('.lobby_cancel_queue_button').addClass('lobby_start_game_button');
        $('.lobby_cancel_queue_button').removeClass('lobby_cancel_queue_button');
        window.clearInterval(interval);
        sec = 0;
        min = 0;
        $('#sec').html('');
        $('#min').html('');
        notificationSocket.close();
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

    $(document).on('click', '.lobby_start_game_button', (event) => {
        event.target.innerHTML = 'Cancel';
        event.target.classList.add('lobby_cancel_queue_button');
        event.target.classList.remove('lobby_start_game_button');
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
        $.ajax({
            method: "get",
            url: "/games/queue/",
            data: {},
            success: (data) => {
                max_players = data.max_players;
                queue_id = data.queue_id;

                notificationSocket = new WebSocket (
                    'ws://' + window.location.host + '/ws/queue/' + queue_id
                );

                notificationSocket.onopen = (e) => {
                    console.log('open')
                    console.log(e)
                }

                notificationSocket.onmessage = (e) => {
                    const data = JSON.parse(e.data)['message'];
                    let action = data['action'];
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
                    } else if(action == 'accept_count' && is_last_player) {
                        accept_count++;
                        if(accept_count == max_players) {
                            $.ajax({
                                method: "get",
                                url: "/games/create_game/",
                                data: {},
                                success: (data) => {
                                    notificationSocket.send(
                                        JSON.stringify({'message': {'action': 'create_game', 'url': data.url}})
                                    )
                                },
                                error: (data) => {
                                }
                            });
                        }
                    } else if(action == 'create_game') {
                        window.location.href = data['url'];
                    };
                };

                notificationSocket.onclose = (e) => {
                    console.log('close')
                    console.log(e);
                }

                notificationSocket.onerror = (e) => {
                    console.log('error')
                    console.log(e)
                }


                if(data.result == 'start') {
                    is_last_player = true;
                    connection_check();
                }
            },
            error: (data) => {
            }
        });
    });

    $(document).on('click', '.lobby_accept_request_button', () => {
        accepted = true;
        notificationSocket.send(
            JSON.stringify({'message': {'action': 'accept_count'}})
        );
    });

    $(document).on('click', '.lobby_cancel_queue_button', () => {
        cancel_queue();
    });

    window.addEventListener('beforeunload', () => {
        quit_lobby();
    });

});