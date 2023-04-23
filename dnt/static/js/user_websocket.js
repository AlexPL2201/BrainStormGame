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
        } else if(action == 'chat_message') {
            let message = JSON.parse(data['message'])[0];
            let message_sender = data['sender'];
            let text = message.fields.text;
            let date = message.fields.created_at.slice(0, 10);
            let time = message.fields.created_at.slice(11, 16);
            if (data['type'] == 'friend') {
                if($('.friend_chat_messages > .chat_date').length == 0 || $('.friend_chat_messages > .chat_date')[0].outerText != date) {
                    $('.friend_chat_messages').prepend(`<span class='chat_date'>${date}</span>`)
                }
                if (message.fields.sender == parseInt(user_id)) {
                    $('.friend_chat_messages').prepend(`<div class='chat_sent'><span class='chat_message_sender'>${message_sender}</span>
                    <span class='chat_message_text'>${text}<span class='chat_message_time'>${time}</span></span></div>`);
                } else {
                    $('.friend_chat_messages').prepend(`<div class='chat_received'><span class='chat_message_sender'>${message_sender}</span>
                    <span class='chat_message_text'>${text}<span class='chat_message_time'>${time}</span></span></div>`);
                }
            } else if (data['type'] == 'lobby'){
                if($('.lobby_chat_messages > .chat_date').length == 0 || $('.lobby_chat_messages > .chat_date')[0].outerText != date) {
                    $('.lobby_chat_messages').prepend(`<span class='chat_date'>${date}</span>`)
                }
                if (message.fields.sender == parseInt(user_id)) {
                    $('.lobby_chat_messages').prepend(`<div class='chat_sent'><span class='chat_message_sender'>${message_sender}</span>
                    <span class='chat_message_text'>${text}<span class='chat_message_time'>${time}</span></span></div>`);
                } else {
                    $('.lobby_chat_messages').prepend(`<div class='chat_received'><span class='chat_message_sender'>${message_sender}</span>
                    <span class='chat_message_text'>${text}<span class='chat_message_time'>${time}</span></span></div>`);
                }
            }
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

    $('.friend_chat_close').on('click', () => {
        $('.friend_chat_block').css('display', '');
    });

    $('.header_friend_chat').on('click', (event) => {
        $('.friend_chat_block').css('display', 'flex');
        let friend_pk = parseInt(event.target.id.replace('chat_friend_', ''));
        $.ajax({
            method: "get",
            url: "/chat/load_messages/",
            data: {friend_pk: friend_pk, type: 'friend'},
            success: (data) => {
                let messages = data['messages'];
                if (messages.length > 0) {
                    let date = messages[0].created_at.slice(0, 10);
                    let html_string = '';
                    for (let message of messages) {
                        let message_date = message.created_at.slice(0, 10);
                        if(date != message_date) {
                            html_string += `<span class='chat_date'>${date}</span>`;
                            date = message_date;
                        }
                        let time = message.created_at.slice(11, 16);
                        if (message.sender_id == parseInt(user_id)) {
                            let message_sender = data['user_nickname'];
                            html_string += `<div class='chat_sent'><span class='chat_message_sender'>${message_sender}</span>
                            <span class='chat_message_text'>${message.text}<span class='chat_message_time'>${time}</span></span></div>`;
                        }else{
                            let message_sender = data['friend_nickname'];
                            html_string += `<div class='chat_received'><span class='chat_message_sender'>${message_sender}</span>
                            <span class='chat_message_text'>${message.text}<span class='chat_message_time'>${time}</span></span></div>`;
                        }
                    };
                    html_string += `<span class='chat_date'>${date}</span>`;
                    $('.friend_chat_messages').html(html_string);
                };
                $('.friend_chat_name').html(data['friend_nickname']);
                $('.friend_chat_textarea').attr('id', `textarea_${friend_pk}`);
            },
            error: (data) => {
            }
        })
    });


    $('.friend_chat_textarea').on('keydown', (event) => {

        if (event.keyCode == 13) {
            event.preventDefault();
            let reciever_pk = parseInt(event.target.id.replace('textarea_', ''));
            let chat_message = event.target.value;
            event.target.value = '';
            $.ajax({
                method: "get",
                url: "/chat/create_messages/",
                data: {sender: user_id, receiver: reciever_pk, message: chat_message, type: 'friend'},
                success: (data) => {

                },
                error: (data) => {
                }
            })
        }
    })



});