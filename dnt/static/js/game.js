window.addEventListener('load', () => {

    // получение id из скрытых инпутов на странице
    let game_id = $('#game_id').val()
    let user_id = $('#user_id').val()

    let chosen_answer;
    let is_answered = false;

    // запуск сокета
    let notificationSocket = new WebSocket (
        'ws://' + window.location.host + '/ws/game/' + game_id
    );

    // метод при открытии сокета
    notificationSocket.onopen = (e) => {
        console.log('open')
        console.log(e)
        // запуск игры на серверной части
        $.ajax({
            method: "get",
            url: "/games/start_game/",
            data: {},
            success: (data) => {
            },
            error: (data) => {
            }
        });
    }

    // метод при получении сообщения
    notificationSocket.onmessage = (e) => {
        // получение объекта сообщения и действия из него
        const data = JSON.parse(e.data)['message'];
        let action = data['action'];

        // получение вопроса и добавление его на страницу
        if(action == 'get_question') {
            chosen_answer = undefined;
            is_answered = false;
            $('.game_question').html(data.question);
            let html_string = '';
            for(let answer of data.answers) {
                html_string += `<p class='game_answer' id='answer_${answer.id}'>${answer.answer}</p>`;
            }
            $('.game_answers_block').html(html_string);
        // получение правильного ответа и добавление его на страницу
        } else if(action == 'get_answer') {
            // обновление таблицы баллов
            for(let [pk, score] of Object.entries(data['score'])) {
                $(`#score_${pk} > .game_score`).html(score);
            };
            // обводка правильного ответа и ответа пользователя, если он не правильный, зелёным и красным соответственно
            $('.chosen_answer').css('border', '1px solid red');
            $(`#answer_${data.correct_answer.id}`).css('border', '1px solid green');
        // переход на страницу с результатами
        } else if(action == 'show_results') {
            window.location.href = data['url'];
        }
    };

    // метод при закрытии сокета (пусто)
    notificationSocket.onclose = (e) => {
        console.log('close')
        console.log(e);
    }

    // метод при ошибке у сокета (пусто)
    notificationSocket.onerror = (e) => {
        console.log('error')
        console.log(e)
    }

    // функция отправки выбранного пользователем ответа на сервер для проверки
    function send_answer() {
        $.ajax({
            method: "get",
            url: "/games/check_answer/",
            data: {answer: chosen_answer},
            success: (data) => {
            },
            error: (data) => {
            }
        });
    }

    // обработчик события нажатия на ответ
    $(document).on('click', '.game_answer', (event) => {
        // если ответ уже отправлен, ничего не происходит
        if(!is_answered) {
            $('.chosen_answer').css('border', '');
            $('.chosen_answer').removeClass('chosen_answer');
            event.target.style.border = '1px solid black';
            event.target.classList.add('chosen_answer');
            chosen_answer = event.target.id.replace('answer_', '');
        }
    });

    // обработчик события нажатия на кнопку отправки ответа
    $(document).on('click', '.game_answer_button', (event) => {
        // если ответ уже отправлен или не выбран, ничего не происходит
        if(chosen_answer && !is_answered) {
            is_answered = true;
            send_answer();
        }
    })

    // обработчик события закрытия окна, перехода на другую страницу или обновления страницы (скорее всего не нужен,
    // создан для решения ошибки, в процессе)
    window.addEventListener('beforeunload', () => {
        notificationSocket.close();
    });

});