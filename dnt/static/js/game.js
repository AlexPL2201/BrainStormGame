window.addEventListener('load', () => {

    let notificationSocket = new WebSocket (
        'ws://' + window.location.host + '/ws/game/' + $('#game_id').val()
    );

    notificationSocket.onopen = (e) => {
        console.log('open')
        console.log(e)
        $.ajax({
            method: "get",
            url: "/games/start_game/",
            data: {},
            success: (data) => {
                console.log(data)
            },
            error: (data) => {
            }
        });
    }

    notificationSocket.onmessage = (e) => {
        const data = JSON.parse(e.data)['message'];
        let action = data['action'];
        console.log(data)
    };

    notificationSocket.onclose = (e) => {
        console.log('close')
        console.log(e);
    }

    notificationSocket.onerror = (e) => {
        console.log('error')
        console.log(e)
    }

});