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
            $('.lobby_invitation_accept').css('display', 'inline');
            $('.lobby_invitation_reject').css('display', 'inline');
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
            $(`#user_${data['quitter_pk']}`).remove();
            $('.lobby_invite_block').css('display', '');
            $('.lobby_invite_block').append(`<span class="lobby_invite_friend" id="friend_${data['quitter_pk']}">${data['quitter_nickname']}</span>`);
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
            $(`#friend_${data['joiner_pk']}`).remove();
            $('.lobby_users').append(`<p id='user_${data["joiner_pk"]}'>${data['joiner_nickname']}</p>`);
            $('#mode_ranked').css('display', 'none');
            if(data['last_place']) {
                $('.lobby_invite_block').css('display', 'none');
            };
        } else if(action == 'add_theme') {
            let html_string = '<select class="lobby_theme">';
            for (let theme of data['themes']) {
                html_string += `<option value='${theme[0]}'>${theme[0]}</option>`
            };
            html_string += '</select>';
            $('body').append(html_string);
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
});