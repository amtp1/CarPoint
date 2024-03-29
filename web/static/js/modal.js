function showLeaveRequestModal(car_id, title, image, subtitle, transmission, type_fuel, wd, engine_volume){
    var modal = $("#lr-modal");
    modal.find(".auto-title").text(title);
    modal.find(".auto-subtitle").text(subtitle);
    modal.find("#transmission").text(transmission);
    modal.find("#type_fuel").text(type_fuel);
    modal.find("#wd").text(wd);
    modal.find("#engine_volume").text(engine_volume.replace(",", "."));
    modal.find("#auto-img").attr("src", image);
    var lv_btn = document.getElementById("leave-request-btn");
    lv_btn.setAttribute("onClick", `javascript: leaveRequest(${car_id});`);
    modal.modal("show");
}

function leaveRequest(car_id){
    var name = $("#name").val();
    var city = $("#city").val();
    var tel = $("#tel1").val();
    var email = $("#email").val();
    var address = $("#address").val();
    if (!name || !city || !tel || !email || !address){
        return alert("Нужно заполнить все поля!");
    }
    var data = new FormData(); // Init new FormData object.
    data.append("car_id", car_id);
    data.append("name", name);
    data.append("city", city);
    data.append("tel", tel);
    data.append("email", email);
    data.append("address", address);
    fetch("leave_request", {
        method: "POST",
        body: data,
        contentType: 'application/json',
        headers: {
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": $.cookie("csrftoken")
        },
    }).then(function (response) {
        response.json().then(
            function (data) {
                if (data["response"]){
                    var modal = $("#lr-modal");
                    modal.modal("hide");
                    return alert("Заявка успешно отправлена!");
                }else{
                    return alert('Количество авто равно 0');
                }
            }
        )
    })
}