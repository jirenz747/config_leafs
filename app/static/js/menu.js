
function change_object(){
    if(! $('#object').val().includes('None')){
        $.post('/change_location', {
        location: $('#object').val()
        }).done(function(response){
            option = '';
            option += '<option value="None"> Choose Rack </option>';
            for(rack in response['racks'])
            {
                option += "<option value="+response['racks'][rack]+">"+response['racks'][rack]+"</option>";
            }
            $('#rack').html(option);
        }).fail(function() {
        alert('error');
        });
    }
    else
    {
        $('#resend_data_qfx').addClass("invisible");
        $('#port_configuration').addClass("invisible");
    }
}

function change_rack(){
    if(! $('#rack').val().includes('None')){
        $('#loading_data').removeClass("invisible");
        $("#loading_data").show();
        $.post('/change_rack', {
            location: $('#object').val(),
            rack: $('#rack').val()
        }).done(function(response){
            $('#container').html(response);
            $('#loading_data').addClass("invisible");
            $('#tab').removeClass("invisible");
            $('#trunk_vlans').hide();
            $('#label_trunk_vlans').hide();
            $('#access_vlan').hide();
            $('#label_access_vlan').hide();
        }).fail(function(error_response) {
            $('#loading_data').addClass("invisible");
        });
    }
    else
    {
        $('#resend_data_qfx').addClass("invisible");
        $('#port_configuration').addClass("invisible");
    }
}

function type_port_change() {
    if($('#type_port').val() == 'access')
    {
        $('#trunk_vlans').val('');
        $('#trunk_vlans').hide();
        $('#label_trunk_vlans').hide();
        $('#access_vlan').show();
        $('#label_access_vlan').show();
    }
    else if($('#type_port').val() == 'trunk')
    {

        $('#trunk_vlans').show();
        $('#label_trunk_vlans').show();
        $('#access_vlan').hide();
        $('#label_access_vlan').hide();
        $('#access_vlan').val('None');
    }
    else
    {
        $('#access_vlan').hide();
        $('#label_access_vlan').hide();
        $('#access_vlan').val('None');
        $('#trunk_vlans').hide();
        $('#label_trunk_vlans').hide();
        $('#trunk_vlans').val('');
    }
}


function submit_new_data(){

        if( $("#port").val().includes('None')){
            alert("Choose port");
        }
        else if($("#type_port").val().includes('None')){
            alert("Choose type port");
        }
        else if($("#object").val().includes('None')){
            alert("Choose object");
        }
        else if($("#rack").val().includes('None')){
            alert("Choose rack");
        }
        else if($("#description").val().length == 0){
            alert("Enter description");
        }
        else if($("#mtu").val().includes('None')){
            alert("Choose mtu");
        }
        else if($("#speed").val().includes('None')){
            alert("Choose speed");
        }
        else if(($("#access_vlan").val().length == 0) && ($('#trunk_vlans').val().length == 0)){
            alert("choose vlans");
        }
        else if(($("#access_vlan").val().includes('None')) && ($('#trunk_vlans').val().length == 0)){
            alert("choose vlans");
        }
        else{
            var vlans;
            if ($("#access_vlan").val().includes('None')){
                vlans = String($('#trunk_vlans').val());
            }
            else{
                vlans = String($('#access_vlan').val());
            }
            $.post('/config_port', {
                location: $('#object').val(),
                rack: $('#rack').val(),
                port: $('#port').val(),
                description: $('#description').val(),
                mtu: $('#mtu').val(),
                speed: $('#mtu').val(),
                type_port: $('#type_port').val(),
                vlan: vlans
            }).done(function(response){
                $('.test').html(response);

            }).fail(function() {
            alert('error');
            });

        }
}

