function initial_load(){
    // console.log(things_data_json)
    console.log(events_data_json)
    events_data=JSON.parse(events_data_json)
    
    const insert_alert=document.getElementById("insert_alerts_log")
    let table_list=""
    
    let zones=[]
    for(one_event of events_data){
        zones.push(one_event.zone)
        if(one_event.event=="wet_device"){
            table_list=table_list+`   
            <tr>
                <td>
                    Moisture detected on the device
               </td>
               <td>${one_event.zone}</td>
               <td >${one_event.datetime}</td>
               <td class="text-danger">
                    High
                </td>
            </tr>`
        }

        if(one_event.event=="strong_wave"){
            table_list=table_list+`   
            <tr>
                <td>
                    Strong wave detected
               </td>
               <td>${one_event.zone}</td>
               <td >${one_event.datetime}</td>
               <td class="text-warning">
                    Medium
                </td>
            </tr>`
        }
    }
    insert_alert.innerHTML=table_list

    const unique_zones = [...new Set(zones)];
    const select_zone=document.getElementById("select_zone")
    let select_zone_options=`<option id="All_Zones"value="All Zones">All Zones</option>`
    for(zone of unique_zones){
        select_zone_options=select_zone_options+`
        <option id="${zone.replace(" ","_")}" value="${zone}">${zone}</option>
        `
    }
    select_zone.innerHTML=select_zone_options
}

initial_load()

function filter_alerts_by_zone(){
    const selected_zone=document.getElementById("select_zone").value
    display_alerts_log(selected_zone)
}

function filter_alerts_by_next_zone(){
    const select_zone=document.getElementById("select_zone")
    console.log(select_zone)
    next_zone_value=document.getElementById(select_zone.value.replace(" ","_")).nextElementSibling.innerText
    select_zone.value=next_zone_value
    console.log(next_zone_value)
    display_alerts_log(next_zone_value)
}

function filter_alerts_by_previous_zone(){
    const select_zone=document.getElementById("select_zone")
    console.log(select_zone)
    next_zone_value=document.getElementById(select_zone.value.replace(" ","_")).previousElementSibling.innerText
    select_zone.value=next_zone_value
    console.log(next_zone_value)
    display_alerts_log(next_zone_value)
}

function display_alerts_log(selected_zone){
    const insert_alert=document.getElementById("insert_alerts_log")
    // things_data=JSON.parse(things_data_json)
    events_data=JSON.parse(events_data_json)
    let table_list=""
    for(one_event of events_data){
        if(one_event.zone!= selected_zone && selected_zone!="All Zones"){
            continue
        }
        if(one_event.event=="wet_device"){
            table_list=table_list+`   
            <tr>
                <td>
                    Moisture detected on the device
               </td>
               <td>${one_event.zone}</td>
               <td >${one_event.datetime}</td>
               <td class="text-danger">
                    High
                </td>
            </tr>`
        }

        if(one_event.event=="strong_wave"){
            table_list=table_list+`   
            <tr>
                <td>
                    Strong wave detected
               </td>
               <td>${one_event.zone}</td>
               <td >${one_event.datetime}</td>
               <td class="text-warning">
                    Medium
                </td>
            </tr>`
        }
    }
    insert_alert.innerHTML=table_list
}


// Initialize and add the map
function initMap() {
    things_data=JSON.parse(things_data_json);
    const map = new google.maps.Map(document.getElementById("map"), {
      zoom: 11,
      center: {lat: 1.3521, lng: 103.8198},
    });
   
    for(thing of things_data){
        let svgMarker
        if(thing.status=="online"){
            svgMarker = {
                path: "M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z",
                fillColor: "green",
                fillOpacity: 0.6,
                strokeWeight: 0,
                rotation: 0,
                scale: 2,
                anchor: new google.maps.Point(15, 30),
                };
        }else{
            svgMarker = {
                path: "M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10zm0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6z",
                fillColor: "red",
                fillOpacity: 0.6,
                strokeWeight: 0,
                rotation: 0,
                scale: 2,
                anchor: new google.maps.Point(15, 30),
                };
        }
    
        const contentString =`
        <p class="map-marker-selected">Location: ${thing.zone}</p>
        <p class="${thing.status=='online'&&'text-success'|| 'text-danger'}">Device Status: ${thing.status}</p>`
        const marker =new google.maps.Marker({
            position: {lat:Number(thing.coordinate.lat), lng:Number(thing.coordinate.lng)},
            icon: svgMarker,
            map: map,
          });
        
        const infowindow = new google.maps.InfoWindow({
        content: contentString,
        });

        marker.addListener("click", () => {
        infowindow.open({
            anchor: marker,
            map,
            shouldFocus: false,
        });
            setTimeout(() => {   
            length=document.getElementsByClassName("map-marker-selected").length
            selected_zone=document.getElementsByClassName("map-marker-selected")[length-1].innerText
            display_alerts_log(selected_zone.replace("Location: ",""))
            document.getElementById("select_zone").value=selected_zone.replace("Location: ","")
            }, 500)

        });
    }
  }