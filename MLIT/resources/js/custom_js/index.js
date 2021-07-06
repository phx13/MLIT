$(document).ready(function () {
    initIndexMap();
})

let map = initMap(ol.proj.fromLonLat([-4.5263671875, 54.303704439898084]), 6);

function initIndexMap() {
    initFeature();
    let popup = initOverlay();
    onOverlayClick(popup);
}

function initFeature() {
    $.when($.get('/data/')).done(function (data) {
        let points = data;
        let iconFeatures = [];
        points.forEach(function (point) {
            for (let key in point) {
                let coordinate = ol.proj.fromLonLat([point[key][0] * 1, point[key][1] * 1])
                let iconFeature = new ol.Feature({
                    geometry: new ol.geom.Point(coordinate),
                    id: key,
                    longitude: point[key][0] * 1,
                    latitude: point[key][1] * 1,
                    address: point[key][2]
                });
                let iconStyle = new ol.style.Style({
                    image: new ol.style.Icon({
                        anchor: [0.5, 0.5],
                        anchorOrigin: 'top',
                        src: '../../images/icons/location.jpg',
                        scale: 0.15
                    })
                });
                iconFeature.setStyle(iconStyle);
                iconFeatures.push(iconFeature);
            }
        });

        let vectorSource = new ol.source.Vector({
            features: iconFeatures
        });

        let vectorLayer = new ol.layer.Vector({
            source: vectorSource
        });

        map.addLayer(vectorLayer);
    });
}

function flyTo(location, done) {
    let duration = 2000;
    let zoom = 6;
    let parts = 2;
    let called = false;

    function callback(complete) {
        --parts;
        if (called) {
            return;
        }
        if (parts === 0 || !complete) {
            called = true;
            done(complete);
        }
    }

    map.getView().animate(
        {
            center: location,
            duration: duration,
        },
        callback
    );
    map.getView().animate(
        {
            zoom: zoom - 1,
            duration: duration / 2,
        },
        {
            zoom: zoom,
            duration: duration / 2,
        },
        callback
    );
}

function initOverlay() {
    let popup = new ol.Overlay({
        element: document.getElementById('popup'),
    });
    map.addOverlay(popup);
    return popup;
}

function onOverlayClick(popup) {
    map.on('click', function (evt) {
        let pixel = map.getEventPixel(evt.originalEvent);
        let feature = map.forEachFeatureAtPixel(pixel, function (feature) {
            return feature;
        });

        if (feature) {
            let element = popup.getElement();
            let coordinate = feature.getProperties()['geometry']['flatCoordinates'];
            let address = feature.getProperties()['address'];
            let longitude = feature.getProperties()['longitude'];
            let latitude = feature.getProperties()['latitude'];
            flyTo(coordinate, function () {
            });

            $(element).popover('dispose');
            popup.setPosition(coordinate);
            $(element).popover({
                container: element,
                placement: 'top',
                animation: false,
                html: true,
                content: '<div class="card" style="width: 18rem;">\n' +
                    '        <img src="/images/thumbs/location.png" class="card-img-top" alt="...">\n' +
                    '        <div class="card-body">\n' +
                    '            <h5 class="card-title" id="locationAddress"></h5>\n' +
                    '            <p class="card-text" id="locationLongitude"></p>\n' +
                    '            <p class="card-text" id="locationLatitude"></p>\n' +
                    '        </div>\n' +
                    '    </div>',
            });
            $(element).popover('show');
            $('#locationAddress').html('<b>Address: </b>' + address);
            $('#locationLongitude').html('<b>Longitude: </b>' + longitude);
            $('#locationLatitude').html('<b>Latitude: </b>' + latitude);
        } else {
            let element = popup.getElement();
            $(element).popover('dispose');
        }
    });
}