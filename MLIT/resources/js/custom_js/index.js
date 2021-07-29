// $(document).ready(function () {
//     initIndexMap();
// })

let map = initMap(ol.proj.fromLonLat([173.02613593120356, -41.55131689740276]), 6);

// map.on('singleclick', function (e) {
//     alert(e.coordinate);
//     alert(ol.proj.transform(e.coordinate, 'EPSG:3857', 'EPSG:4326'));
//
//     alert(map.getEventCoordinate(e.originalEvent));
//     alert(ol.proj.transform(map.getEventCoordinate(e.originalEvent), 'EPSG:3857', 'EPSG:4326'));
//
//     var lonlat = map.getCoordinateFromPixel(e.pixel);
//     alert(lonlat);
//     alert(ol.proj.transform(lonlat, "EPSG:3857", "EPSG:4326"));
// })

function updateLocationData() {
    let dataType = $('#updateDataSelect').val();
    $("#updateDataBtn").attr("disabled", true);
    $.get('/update/' + dataType + '/', function (data) {
        alert('Update ' + dataType + ' data successfully');
        $("#updateDataBtn").attr("disabled", false);
    });
}

function displayLocationData() {
    let dataType = $('#displayDataSelect').val();

    initFeature(dataType);
    let popup = initOverlay();
    onOverlayClick(popup);
}

function initTable() {
    $('#btTable').bootstrapTable({
        url: '/train/data/',  // 请求数据源的路由
        dataType: "json",
        pagination: true, //前端处理分页
        singleSelect: false,//是否只能单选
        search: true, //显示搜索框，此搜索是客户端搜索，不会进服务端，所以，个人感觉意义不大
        // toolbar: '#toolbar-' + courseid, //工具按钮用哪个容器#}
        striped: true, //是否显示行间隔色
        cache: false, //是否使用缓存，默认为true，所以一般情况下需要设置一下这个属性（*）
        pageNumber: 1, //初始化加载第10页，默认第一页
        pageSize: 10, //每页的记录行数（*）
        pageList: [10, 20, 50, 100], //可供选择的每页的行数（*）
        strictSearch: true,//设置为 true启用 全匹配搜索，false为模糊搜索
        // showColumns: true, //显示内容列下拉框
        // showRefresh: true, //显示刷新按钮
        minimumCountColumns: 2, //当列数小于此值时，将隐藏内容列下拉框
        // clickToSelect: true, //设置true， 将在点击某行时，自动勾选rediobox 和 checkbox
        // height: 500, //表格高度，如果没有设置height属性，表格自动根据记录条数决定表格高度
        uniqueId: "id", //每一行的唯一标识，一般为主键列
        showToggle: true, //是否显示详细视图和列表视图的切换按钮
        // cardView: true, //是否显示详细视图
        // detailView: true, //是否显示父子表，设置为 true 可以显示详细页面模式,在每行最前边显示+号#}
        sidePagination: "client", //分页方式：client客户端分页，server服务端分页（*）
        columns: [
            {
                title: "selectAll",
                field: "select",
                checkbox: true,
                align: "center",
                cellStyle: function () {
                    $(".th-inner")[0].style.overflow = "inherit";
                    return {css: {"overflow": "inherit"}}
                }
            }, {
                field: 'id',
                title: 'Id'
            }, {
                field: 'module',
                title: 'Module'
            }, {
                field: 'question',
                title: 'Question'
            }, {
                field: 'description',
                title: 'Description'
            }, {
                field: 'type',
                title: 'Type'
            }, {
                field: 'option',
                title: 'Option',
                formatter: function (value, row, index) {
                    return value.split("|").join(" ");
                }
            }, {
                field: 'answer',
                title: 'Answer'
            }, {
                field: 'release_time',
                title: 'Release Time'
            }, {
                field: 'operation',
                title: 'Operation',
                formatter: function (value, row, index) {
                    return '<button class="btn btn-outline-primary" data-toggle="modal" data-target="#questionDetail" onclick="editQuestion(' + row.id + ')">edit</button>'
                }
            }, {
                field: 'review',
                title: 'Review',
                formatter: function (value, row, index) {
                    let reviewUrl = "{{ url_for('satisfaction_result_bp.question_review_result',id='questionId' ) }}".replace('questionId', row.id);
                    return '<a class="btn btn-outline-primary" href="' + reviewUrl + '">review</a>'
                }
            }]
    });
}

function initFeature(dataType) {
    $('#totalCount').text("");
    $('#recognizedCount').text("");
    $('#geocodedCount').text("");
    let currentLayers = map.getLayers()['array_'];
    let layerCount = map.getLayers()['array_'].length;
    if (layerCount > 1) {
        map.removeLayer(currentLayers[layerCount - 1]);
    }
    $.when($.get('/display/' + dataType)).done(function (data) {
        $('#totalCount').text(data["total_count"]);
        $('#recognizedCount').text(data["recognized_count"]);
        $('#geocodedCount').text(data["geocoded_count"]);

        let points = data["etl_locations"];
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
        alert('Display successfully');
    });
}

function flyTo(location, done) {
    let duration = 2000;
    let zoom = 7;
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

function trainModel() {
    let modelType = $('#trainModelSelect').val();
    $("#trainModelBtn").attr("disabled", true);
    $.get('/train/model/' + modelType + '/', function (data) {
        alert(data);
        $("#trainModelBtn").attr("disabled", false);
    });
}

function trainData() {
    let dataType = $('#trainDataSelect').val();
    $("#trainDataBtn").attr("disabled", true);
    $.get('/train/data/' + dataType + '/', function (data) {
        alert(data);
        $("#trainDataBtn").attr("disabled", false);
    });
}