function edit_port(data){

    var port = $(data).val();
    var init_description = '#init_description_' + port;
    var init_speed = '#init_speed_' + port;
    var init_mtu = '#init_mtu_' + port;
    var init_port_mode = '#init_port_mode_' + port;
    var init_vlan = '#init_vlan_' + port;
    var mtu = '#init_mtu_' + port;
    var type = '#init_type_port_' + port;
    var vlan = '#init_vlan_' + port;
    var edit_port = '#edit_port_' + port;
    var change_description = '#change_description_' + port;
    var change_speed = '#change_speed_' + port;
    var change_mtu = '#change_mtu_' + port;
    var change_port_mode = '#change_port_mode_' + port;
    var change_access_vlan = '#change_access_vlan_' + port;
    var change_trunk_vlan = '#change_trunk_vlan_' + port;
    var reset_port = '#reset_port_' + port;
    $('.test').html($(init_port_mode).text());

    $(init_description).hide();
    $(change_description).removeClass('d-none');
    $(init_speed).hide();
    $(change_speed).removeClass('d-none');
    $(init_mtu).hide();
    $(change_mtu).removeClass('d-none');
    $(init_port_mode).hide();
    $(change_port_mode).removeClass('d-none');

    $(edit_port).addClass('edited');
    $(edit_port).addClass('d-none');
    $(reset_port).removeClass('d-none');

    if($(init_port_mode).text() == 'access')
    {
        $(init_vlan).hide();
        $(change_access_vlan).removeClass('d-none');
    }
    else if($(init_port_mode).text() == 'none')
    {
        $(init_vlan).hide();
        $(change_access_vlan).removeClass('d-none');
    }
    else
    {
        $(init_vlan).hide();
        $(change_trunk_vlan).removeClass('d-none');
    }

}

function reset_port(data){

    var port = $(data).val();
    var init_description = '#init_description_' + port;
    var init_speed = '#init_speed_' + port;
    var init_mtu = '#init_mtu_' + port;
    var init_port_mode = '#init_port_mode_' + port;
    var init_vlan = '#init_vlan_' + port;
    var mtu = '#init_mtu_' + port;
    var type = '#init_type_port_' + port;
    var vlan = '#init_vlan_' + port;
    var edit_port = '#edit_port_' + port;
    var change_description = '#change_description_' + port;
    var change_speed = '#change_speed_' + port;
    var change_mtu = '#change_mtu_' + port;
    var change_port_mode = '#change_port_mode_' + port;
    var change_access_vlan = '#change_access_vlan_' + port;
    var change_trunk_vlan = '#change_trunk_vlan_' + port;
    var reset_port = '#reset_port_' + port;
    $(init_description).show();
    $(change_description).addClass('d-none');
    $(init_speed).show();
    $(change_speed).addClass('d-none');
    $(init_mtu).show();
    $(change_mtu).addClass('d-none');
    $(init_port_mode).show();
    $(change_port_mode).addClass('d-none');
    $(init_vlan).show();
    $(change_access_vlan).addClass('d-none');
    $(change_trunk_vlan).addClass('d-none');

    $(edit_port).removeClass('edited');
    $(edit_port).removeClass('d-none');
    $(reset_port).addClass('d-none');
}

function test2(data){

    var port = $(data).attr('id').replace('change_port_mode_','')
    var port_mode = $(data).val();
    $('.port_mode_test').html($(data).val());
    var change_trunk_vlan = '#change_trunk_vlan_' + port;
    var change_access_vlan = '#change_access_vlan_' + port;
    var init_vlan = '#init_vlan_' + port;

    if (port_mode == 'access'){
            $(init_vlan).hide();
            $(change_trunk_vlan).addClass('d-none');
            $(change_access_vlan).removeClass('d-none');
    }
    else{
            $(init_vlan).hide();
            $(change_trunk_vlan).removeClass('d-none');
            $(change_access_vlan).addClass('d-none');
    }

}

function commit()
{
    var a = $('.port').text().split('_');
    var init_description;
    var init_speed;
    var init_mtu;
    var init_port_mode;
    var init_vlan;
    var change_description;
    var change_speed;
    var change_mtu;
    var change_port_mode;
    var change_vlan;
    var port;
    var edit_port;
    var interface = {};
    var interfaces = [];
    var count_edit_port = 0;
    var count_interfaces = 0;
    for(var i=0; i< a.length - 1; i++)
    {
        var triger = 0;
        port = a[i].replace(/\//g, '-');
        init_description = $('#init_description_' + port).text();
        init_speed = $('#init_speed_' + port).text();
        init_mtu = $('#init_mtu_' + port).text();
        init_port_mode = $('#init_port_mode_' + port).text();
        init_vlan = $('#init_vlan_' + port).text();
        change_description = $('#change_description_' + port).val();
        change_speed = $('#change_speed_' + port).val();
        change_mtu = $('#change_mtu_' + port).val();
        change_port_mode = $('#change_port_mode_' + port).val();
        if($('#edit_port_'+ port).length == 0){
            continue;
        }
    edit_port = $('#edit_port_' + port).attr("class");
    if(edit_port.search('edited') != -1)
    {
        count_edit_port++;
        $('.test3').append(edit_port + "<br>");
        $('.test3').append(port + "<br>");
        $('.test3').append(change_description + ' ');
        $('.test3').append(init_description + "<br>");
        $('.test3').append(change_speed + ' ');
        $('.test3').append(init_speed + "<br>");
        $('.test3').append(change_mtu + ' ');
        $('.test3').append(init_mtu + "<br>");
        $('.test3').append(change_port_mode + ' ');
        $('.test3').append(init_port_mode + "<br>");
        if (change_port_mode == 'access')
        {
            change_vlan = $('#change_access_vlan_' + port).val();
            if(!init_vlan.includes(change_vlan)){

                console.log('test - 1');
                triger = 1;
            }
        }
        else
        {
            change_vlan = $('#change_trunk_vlan_' + port).val();
            array_init_vlan = init_vlan.replace(/'/g, '');
            array_init_vlan = array_init_vlan.replace(/\]/g, '');
            array_init_vlan = array_init_vlan.replace(/\[/g, '');
            array_init_vlan = array_init_vlan.split(',');
            for(j=0; j< change_vlan.length; j++)
            {
                if(! init_vlan.includes(change_vlan[j]))
                {
                    console.log('test - 2');
                    triger = 1;
                }
            }
            if(array_init_vlan.length != change_vlan.length)
            {
                triger = 1;
                console.log('test - 3');
            }
        }
        if(change_description != init_description)
        {
            triger = 1;
            console.log('test - 4');
        }
        if(init_speed != change_speed)
        {
            triger = 1;
            console.log('test - 5');
        }
        if(init_mtu != change_mtu)
        {
            triger = 1;
            console.log('test - 6');
        }
        if(init_port_mode != change_port_mode)
        {
            triger = 1;
            console.log('test - 7');
        }

        if(change_vlan.length == 0)
        {
            triger = 0;

        }
        if(triger == 1)
        {

            count_interfaces++;
            interface[port] = {
                'speed': change_speed,
                'mtu': change_mtu,
                'port_mode': change_port_mode,
                'description': change_description,
                'vlan': change_vlan
                };
        }
    }
}

       console.log(count_interfaces);
       console.log(count_edit_port);
    if(count_interfaces != 0 && count_edit_port != 0){
    if ((!$.isEmptyObject(interface))) {
        console.log('yes');
        $('#commit').removeClass("invisible");
        $("#commit").show();
        $.post('/configs_ports', {
            interfaces: JSON.stringify(interface),
            rack: $('#rack').val(),
            location: $('#object').val()
        }).done(function(response){
            $('.test').html(response);
            var interface = {};
            $('#commit').addClass("invisible");
            change_rack();
        }).fail(function() {
        alert('error');
        });
    }
}
}

function test_toast()
{
    $('.toast').toast(option);
}
