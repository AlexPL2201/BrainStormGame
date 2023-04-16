window.addEventListener('load', () => {

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
            $('.lobby_invitation_block').css('display', 'flex');
        } else if(action == 'queue') {
            // необходимые изменения интерфейса
            $('.lobby_start_game_span').html('Отменить поиск');
            $('.lobby_start_game_span').addClass('lobby_cancel_queue_button');
            $('.lobby_start_game_span').removeClass('lobby_start_game_span');

            start_count();
            create_queue_socket(data['queue_id']);
        } else if(action == 'cancel_queue') {
            cancel_queue(false);
        } else if(action == 'player_quit') {
            current_players -= 1;
            $(`#user_${data['quitter_pk']}`).remove();
            $(`#invite_friend_${data['quitter_pk']}`).addClass('header_friend_invite');
            $(`#invite_friend_${data['quitter_pk']}`).removeClass('header_friend_invited');
            $('.header_friend_invite').css('display', '');
            let blank_string = '<div class="lobby_player_blank"></div>';
            if(current_players % 2 == 1) {
                $('.lobby_the_player').before(blank_string);
            } else {
                $('.lobby_the_player').after(blank_string);
            }
            if(data['lobby_leader'] && data['new_leader_pk'] == user_id) {
                $('.lobby_start_game_span').addClass('lobby_start_game_button');
                $('.lobby_start_game_span').removeClass('lobby_start_game_span');
                $('.lobby_change_mode').css('display', '');
                $('.lobby_change_mode').val(data['current_mode']).change();
            };
            if(data['u_r_alone']) {
                $('#mode_ranked').css('display', '');
            };
        } else if(action == 'player_join') {
            current_players += 1;
            $(`#invite_friend_${data['quitter_pk']}`).removeClass('header_friend_invite');
            $(`#invite_friend_${data['quitter_pk']}`).addClass('header_friend_invited');
            let player_string = `<div id='user_${data["joiner_pk"]}' class="lobby_player_block">${data['joiner_nickname']}</div>`;
            if(current_players % 2 == 1) {
                $('.lobby_players_block>div:first-child').remove();
                $('.lobby_the_player').before(player_string);
            } else {
                $('.lobby_players_block>div:last-child').remove();
                $('.lobby_the_player').after(player_string);
            }
            $('#mode_ranked').css('display', 'none');
            if(data['last_place']) {
                $('.header_friend_invite').css('display', 'none');
            };
        } else if(action == 'add_theme') {
            let html_string = '<span>Выберите тему для игры:</span><select class="lobby_theme">';
            for (let theme of data['themes']) {
                html_string += `<option value='${theme[0]}'>${theme[0]}</option>`
            };
            html_string += '</select>';
            $('.lobby_mode').append(html_string);
        } else if(action == 'delete_theme') {
            $('.lobby_theme').remove();
        }
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

    $(document).on('click', '.header_friends_button', (event) => {
        if ($('.header_friends_block').css('display') == 'none') {
            $('.header_friends_block').css('display', 'flex');
        } else if (event.target.classList[0] == 'header_friends_button') {
            $('.header_friends_block').css('display', '');
        }   
    })

    $(document).on('click', '.lobby_invitation_accept', () => {
        $.ajax({
            method: "get",
            url: "/games/join_lobby_ajax/",
            data: {sender_id: sender['pk']},
            success: (data) => {
                userSocket.send(
                    JSON.stringify({'message': {'action': 'accept'}})
                );
                if(data != 'full') {
                    window.location.href = data['url'];
                } else {
                    sender = undefined;
                    $('.lobby_invitation_nickname').html('');
                    $('.lobby_invitation_block').css('display', 'none');
                };
            },
            error: (data) => {
            }
        });
    });

    $(document).on('click', '.lobby_invitation_reject', () => {
        sender = undefined;
        $('.lobby_invitation_nickname').html('');
        $('.lobby_invitation_block').css('display', '');
        userSocket.send(
            JSON.stringify({'message': {'action': 'reject'}})
        );
    });
});